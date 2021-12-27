import re

BIBLE_BOOK_MAPPING = {'01': 'Genesis',
                      '02': 'Exodus',
                      '03': 'Leviticus',
                      '04': 'Numbers',
                      '05': 'Deuteronomy',
                      '06': 'Joshua',
                      '07': 'Judges',
                      '08': 'Ruth',
                      '09': '1 Samuel',
                      '10': '2 Samuel',
                      '11': '1 Kings',
                      '12': '2 Kings',
                      '13': '1 Chronicles',
                      '14': '2 Chronicles',
                      '15': 'Ezra',
                      '16': 'Nehemiah',
                      '17': 'Esther',
                      '18': 'Job',
                      '19': 'Psalms',
                      '20': 'Proverbs',
                      '21': 'Ecclesiastes',
                      '22': 'Song of Solomon',
                      '23': 'Isaiah',
                      '24': 'Jeremiah',
                      '25': 'Lamentations',
                      '26': 'Ezekiel',
                      '27': 'Daniel',
                      '28': 'Hosea',
                      '29': 'Joel',
                      '30': 'Amos',
                      '31': 'Obadiah',
                      '32': 'Jonah',
                      '33': 'Micah',
                      '34': 'Nahum',
                      '35': 'Habakkuk',
                      '36': 'Zephaniah',
                      '37': 'Haggai',
                      '38': 'Zechariah',
                      '39': 'Malachi',
                      '40': 'Matthew',
                      '41': 'Mark',
                      '42': 'Luke',
                      '43': 'John',
                      '44': 'Acts',
                      '45': 'Romans',
                      '46': '1 Corinthians',
                      '47': '2 Corinthians',
                      '48': 'Galatians',
                      '49': 'Ephesians',
                      '50': 'Philippians',
                      '51': 'Colossians',
                      '52': '1 Thessalonians',
                      '53': '2 Thessalonians',
                      '54': '1 Timothy',
                      '55': '2 Timothy',
                      '56': 'Titus',
                      '57': 'Philemon',
                      '58': 'Hebrews',
                      '59': 'James',
                      '60': '1 Peter',
                      '61': '2 Peter',
                      '62': '1 John',
                      '63': '2 John',
                      '64': '3 John',
                      '65': 'Jude',
                      '66': 'Revelation'}


class TextFile:
    def __init__(self, fpath):
        with open(fpath) as f:
            text = f.read()

        self.fname = fpath.split('/')[-1]
        self.text = re.sub('[\n]', ' ', text)
        # self.sents = nltk.sent_tokenize(self.text)
        # self.sents = re.split('\d\d:\d\d\d:\d\d\d', self.text)

        # WE WILL BE USING THE VERSE AS THE ATOMIC UNIT INSTEAD OF A SENTENCE
        verses = [verse.split(" ", maxsplit=1)
                  for verse in self.text.split("  ")]
        # filter out any [''] entries from verses
        self.verses = list(filter(lambda x: len(x) == 2, verses))

    def get_verses(self, query=None):
        '''
        Takes in a query and returns list of verses that contain the specified keyword or keywords
        '''
        query = query.lower().strip()
        # query_set = set([key.lower().strip() for key in query.split(',')])
        query_verses = []
        # Iterate through the sentences and return those that contain the keyword
        for book_chapNum_verseNum, verse in self.verses:
            # left-matching regex (ie will catch 'serpents' when query is 'serpent')
            if re.search(fr'\b{query}', verse.lower()):
                query_verses.append((book_chapNum_verseNum, verse))
        return query_verses

    # def get_sents(self, query=None):
    #     '''
    #     Takes in a query and returns list of verses that contain the specified keyword or keywords
    #     '''
    #     query = query.lower().strip()
    #     # query_set = set([key.lower().strip() for key in query.split(',')])
    #     query_verses = []
    #     # Iterate through the sentences and return those that contain the keyword
    #     for loc_in_bible, verse in self.verses:
    #         # Removes all punctuation from the sentence and then splits it into a list of tokens
    #         # Check if the set of keyword(s) is contained in the set of tokens for that sentence
    #         if query in set(re.sub(r'[^\w\s]', '', verse.lower()).split()):
    #             query_verses.append((loc_in_bible, verse))
    #     return query_verses

    # @staticmethod
    # def get_nearest_neighbors(sents, query, window=5):
    #     '''
    #     Returns a list of passages of length 'window' containing the query. For 'concordance view'
    #     '''

    #     # TODO: Currently it returns just the tokens from the preprocessed list without the punctuation marks. Find a way to return the passage from the
    #     #       original sents list containing punctuation marks

    #     results = []

    #     for sent in sents:

    #         # Filter out punctuation and split sentence into list of tokens
    #         sent_clean = re.sub(r'[^\w\s]', '', sent.lower()).split()

    #         # get the index of the word in that sentence
    #         word_idx = sent_clean.index(query)

    #         # Set the lower and upper index bound for indexing the segment containing 'dogma'

    #         # If the sentence length is less than the window
    #         if len(sent_clean) < window:
    #             results.append(' '.join(sent_clean))

    #         # if the word_idx is at the end of the sentence
    #         elif len(sent_clean) - word_idx <= (window - 1) // 2:

    #             q = len(sent_clean) - word_idx
    #             lower_idx = word_idx - (window - q)
    #             results.append(' '.join(sent_clean[lower_idx:]))

    #         # if word_idx is at beginning of sentence
    #         elif word_idx - (window - 1) // 2 < 0:

    #             upper_bound = window - word_idx
    #             results.append(' '.join(sent_clean[: upper_bound]))

    #         # if word_idx is in middle of sentence
    #         else:
    #             lower_idx = word_idx - (window - 1) // 2
    #             upper_idx = word_idx + (window - 1) // 2
    #             results.append(' '.join(sent_clean[lower_idx: upper_idx + 1]))

    #     return results

    # def concordance(self, window=None):
    #     '''
    #     Returns concordance view where each instance of a word occurrence is accompanied with specified window number of surrounding words
    #     '''
    #     # STEPS:
    #     # 1. Obtain list of tokens eligible for inclusion in Concordance (ie all non-stopwords)
    #     # 2. Get all occurrences of those words by calling get_sents(word) on each
    #     # 3. Get the closest several words for each occurrence, as determined by 'window'

    #     # initialize concord_dict, the dictionary that acts as the concordance
    #     concord_dict = {}

    #     # list of all words/tokens in the text
    #     tokens = set(re.sub(r'[^\w\s]', '', self.text.lower()).split())

    #     # All the stopwords have punctuation removed because all of our tokens have punctuation removed
    #     stopwords_l = set(map(lambda x: re.sub(
    #         r'[^\w\s]', '', x), stopwords.words('english')))

    #     # filter out stopwords; the remaining words will be the entries in the Concordance we're about to build
    #     tokens = [token for token in tokens if token not in stopwords_l]

    #     for token in tokens:
    #         sents = self.get_sents(token)
    #         # sents = re.sub(r'[^\w\s]','',sents.lower()).split()

    #         # Get list of results where each element is a passage containing the token occurrence
    #         results = self.get_nearest_neighbors(sents, token, window=5)

    #         # Add it to dictionary
    #         concord_dict[token] = results

    #     return concord_dict
