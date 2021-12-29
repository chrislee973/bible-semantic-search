import youtube_dl
import requests
from time import sleep
import random

from dotenv import load_dotenv
import streamlit as st

load_dotenv()

ASSEMBLY_KEY = st.secrets["ASSEMBLY_API_KEY"]


class AssemblyTranscript:
    """
    Accepts either a youtube url or a url pointing to an audio file (ie mp3 file) and will return the transcript of that video or audio file
    """
    HEADERS = {
        "authorization": "e73a9f65699f4b3c83ff4a97271118e8",
        "content-type": "application/json"
    }
    HEADERS_AUTH_ONLY = {
        "authorization": "e73a9f65699f4b3c83ff4a97271118e8"
    }
    UPLOAD_ENDPOINT = 'https://api.assemblyai.com/v2/upload'
    TRANSCRIPT_ENDPOINT = "https://api.assemblyai.com/v2/transcript"
    CHUNK_SIZE = 5242880

    def __init__(self, url: str):
        self.url = url
        self.transcript_id = None  # will be populated by submit_to_endpoint()
        self.polling_status = ""  # will be populated by poll_endpoint()

    def submit_to_endpoint(self, transcript_request, start=0, end=0):
        """
        Submits the audio url or the locally saved audio file to the transcript endpoint.
        """
        transcript_response = requests.post(
            self.TRANSCRIPT_ENDPOINT, json=transcript_request, headers=self.HEADERS)
        self.transcript_id = transcript_response.json()['id']
        print("Transcript submitted for processing")
        print("Transcript submission response: \n", transcript_response.json())
        # return transcript_response

    def poll_endpoint(self):
        """
        Polls endpoint, returning the status of the request (one of ["completed", "error", "processing", "queued"])
        """
        if not self.transcript_id:
            raise ValueError(
                "Transcript id not found. Make sure to first submit media to transcript endpoint to obtain transcript id from Assembly, and then poll the transcript endpoint.")

        polling_response = requests.get(
            self.TRANSCRIPT_ENDPOINT + "/" + self.transcript_id, headers=self.HEADERS)
        self.polling_status = polling_response.json(
        )['status']  # update polling_status property
        return polling_response

    def get_transcript_text(self, transcript_id=None, start=0, end=0):
        """
        Returns the transcript from Assembly once Assembly has finished processing the audio
        If transcript_id is provided, grabs the transcript text from Assembly. If not provided, submit the transcript request to the endpoint.
        """
        # IF SELF.TRANSCRIPT_ID ALREADY EXISTS, FETCH THE TRANSCRIPT (IE FOR CASES WHERE YOU WANT TO FETCH THE TRANSCRIPT OF A VIDEO THAT'S ALREADY BEEN PROCESSED)
        if not self.transcript_id:
            transcript_request = self.get_transcript_request(start, end)
            self.submit_to_endpoint(transcript_request)
        else:
            self.transcript_id = transcript_id
        if not self.polling_status:
            self.poll_endpoint()
        while self.polling_status != "completed":
            if self.polling_status == 'error':
                raise ValueError("Polling error")
            self.poll_endpoint()
            sleep(5)  # poll endpoint every 5 seconds until transcript is ready
            print("File is ", self.polling_status)
        print("Transcript ready!")
        # return the transcript
        return self.poll_endpoint().json()['text']

    def get_paragraphs(self):
        if not self.transcript_id:
            raise ValueError(
                "Transcript id not found. Make sure media has been submitted and processed by Assembly, and then poll the transcript endpoint.")
        endpoint = self.TRANSCRIPT_ENDPOINT + "/" + self.transcript_id + "/paragraphs"
        response = requests.get(endpoint, headers=self.HEADERS_AUTH_ONLY)
        return response.json()

    def get_sentences(self):
        if not self.transcript_id:
            print("Transcript id not found. Make sure to first submit media to transcript endpoint to obtain transcript id from Assembly, and then poll the transcript endpoint.")
            return
        endpoint = self.TRANSCRIPT_ENDPOINT + "/" + self.transcript_id + "/sentences"
        response = requests.get(endpoint, headers=self.HEADERS_AUTH_ONLY)
        return response.json()

    def generate_dict(self, context_size='paragraph'):
        """
        Generates list of dictionaries of each paragraph. Dict has keys 'id', 'context', and 'start'.
        Each paragraph will have a random 7 letter alphanumeric key generated for it.
        This dict is what is what will be fed into controller.upsert()
        """
        if context_size == 'paragraph':
            # a list of paragraphs
            paragraphs = self.get_paragraphs()['paragraphs']
            return [{'context': i['text'], 'start (ms)': i['start'], 'id': self._generate_random_id(7)} for i in paragraphs]
        elif context_size == "sentence":
            sentences = self.get_sentences()['sentences']
            return [{'context': i['text'], 'start (ms)': i['start'], 'id': self._generate_random_id(7)} for i in sentences]

    def _generate_random_id(self, num_chars):
        """
        Generates random alphanumeric sequence of length num_chars
        """
        chars = 'abcdefghijklmnopqrstuvwxyz1234567890'
        return ''.join(random.sample(chars, num_chars))


class AudioFileUrl(AssemblyTranscript):
    def __init__(self, url):
        super().__init__(url)

    def get_transcript_request(self, start=0, end=0):
        """
        Rreturns a dictionary containing all the fields needed to submit to the transcript endpoint. 
        This dictionary will eventually be the json payload sent to the Assembly Transcript endpoint in submit_to_endpoint().
        """
        transcript_request = {'audio_url': self.url,
                              "language_model": "assemblyai_media",
                              "audio_start_from": start,
                              "audio_end_at": end}
        return transcript_request


class YouTubeUrl(AssemblyTranscript):
    def __init__(self, url):
        super().__init__(url)

    def save_youtube_audio(self, start=0, end=0):
        """
        Downloads and saves the youtube audio file locally as mp3 file, returning the name of the saved mp3 file
        """
        # download the audio of the YouTube video locally
        meta = self._get_vid(self.url)
        save_location = meta['id'] + ".mp3"

        print('Saved mp3 to', save_location)
        return save_location

    def _get_vid(self, _id):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg-location': './files',
            'outtmpl': "./files/%(id)s.%(ext)s",
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(_id)

    def _read_file(self, filename):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(self.CHUNK_SIZE)
                if not data:
                    break
                yield data

    def get_transcript_request(self, start=0, end=0):
        """
        Saves the audio file of the video locally, and then uploads the audio file to Assembly's CDN. 
        Once uploaded, we receive the url to our audio on Assembly's CDN. 
        The function returns a dictionary containing all the fields needed to submit to the transcript endpoint. 
        This dictionary will eventually be the json payload sent to the Assembly Transcript endpoint in submit_to_endpoint().
        """
        save_location = self.save_youtube_audio()
        print("Uploading audio file to Assembly")
        upload_response = requests.post(
            self.UPLOAD_ENDPOINT, headers=self.HEADERS_AUTH_ONLY, data=self._read_file(save_location))
        audio_url = upload_response.json()['upload_url']
        print('Uploaded to Assmembly at', audio_url)
        transcript_request = {
            'audio_url': audio_url,
            "language_model": "assemblyai_media",
            "audio_start_from": start,
            "audio_end_at": end
        }
        return transcript_request


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=KbCXcOn7P1A"
    yt = YouTubeUrl(url)
    yt.save_youtube_audio()
