from fuzzywuzzy import fuzz
from fuzzywuzzy import process

THRESHOLD = 80

def compare(text, pattern):
    a = fuzz.ratio(text, pattern)
    return a > THRESHOLD, a
