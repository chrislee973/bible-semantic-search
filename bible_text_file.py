import re

BIBLE_BOOK_MAPPING = {
    "01": "Genesis",
    "02": "Exodus",
    "03": "Leviticus",
    "04": "Numbers",
    "05": "Deuteronomy",
    "06": "Joshua",
    "07": "Judges",
    "08": "Ruth",
    "09": "1 Samuel",
    "10": "2 Samuel",
    "11": "1 Kings",
    "12": "2 Kings",
    "13": "1 Chronicles",
    "14": "2 Chronicles",
    "15": "Ezra",
    "16": "Nehemiah",
    "17": "Esther",
    "18": "Job",
    "19": "Psalms",
    "20": "Proverbs",
    "21": "Ecclesiastes",
    "22": "Song of Solomon",
    "23": "Isaiah",
    "24": "Jeremiah",
    "25": "Lamentations",
    "26": "Ezekiel",
    "27": "Daniel",
    "28": "Hosea",
    "29": "Joel",
    "30": "Amos",
    "31": "Obadiah",
    "32": "Jonah",
    "33": "Micah",
    "34": "Nahum",
    "35": "Habakkuk",
    "36": "Zephaniah",
    "37": "Haggai",
    "38": "Zechariah",
    "39": "Malachi",
    "40": "Matthew",
    "41": "Mark",
    "42": "Luke",
    "43": "John",
    "44": "Acts",
    "45": "Romans",
    "46": "1 Corinthians",
    "47": "2 Corinthians",
    "48": "Galatians",
    "49": "Ephesians",
    "50": "Philippians",
    "51": "Colossians",
    "52": "1 Thessalonians",
    "53": "2 Thessalonians",
    "54": "1 Timothy",
    "55": "2 Timothy",
    "56": "Titus",
    "57": "Philemon",
    "58": "Hebrews",
    "59": "James",
    "60": "1 Peter",
    "61": "2 Peter",
    "62": "1 John",
    "63": "2 John",
    "64": "3 John",
    "65": "Jude",
    "66": "Revelation",
}


class BibleTextFile:
    def __init__(self, fpath):
        with open(fpath) as f:
            text = f.read()

        self.fname = fpath.split("/")[-1]
        self.text = re.sub("[\n]", " ", text)

        verses = [verse.split(" ", maxsplit=1) for verse in self.text.split("  ")]
        # filter out any [''] entries from verses
        self.verses = list(filter(lambda x: len(x) == 2, verses))

    def get_verses(self, query=None):
        """
        Takes in a query and returns list of verses that contain the specified keyword or keywords
        """
        query = query.lower().strip()
        query_verses = []
        # Iterate through the sentences and return those that contain the keyword
        for book_chapNum_verseNum, verse in self.verses:
            # left-matching regex (ie will catch 'serpents' when query is 'serpent')
            if re.search(rf"\b{query}", verse.lower()):
                query_verses.append((book_chapNum_verseNum, verse))
        return query_verses
