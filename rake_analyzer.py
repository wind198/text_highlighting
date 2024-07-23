from constant import default_punctuations
from helpers import merge_chunks
import spacy
from rake_nltk import Rake
from nltk.corpus import stopwords
from langdetect import detect
import nltk

nlp = spacy.load("en_core_web_sm")

nltk.download("stopwords")


def is_overlapping(new_position, positions):
    new_start, new_end = new_position
    for start, end in positions:
        # Check if there is an overlap
        if not (new_end <= start or new_start >= end):
            return True
    return False


max_merge_iterations = 3


def extract_keywords(text: str, min_length: int, max_length: int):
    try:
        language = detect(text)
    except:
        language = "unknown"

    # Proceed only if the text is in English
    if language != "en":
        return []  # Return an empty list if the text is not in English

    stop_words = stopwords.words("english")
    stop_words.append("-")
    rake = Rake(min_length=min_length, max_length=max_length, stopwords=[])

    rake.extract_keywords_from_text(text)
    keywords = rake.get_ranked_phrases()

    # Create a list to hold tuples of (keyword, position)
    keyword_positions = []
    text_lower = text.lower()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        start = 0
        while True:
            position = text_lower.find(keyword_lower, start)
            if position == -1:
                break
            new_position = (position, position + len(keyword_lower))
            # Check if the new position overlaps with any existing positions
            if is_overlapping(new_position, keyword_positions):
                start = position + len(keyword_lower)
                continue
            keyword_positions.append(new_position)
            start = position + len(keyword_lower)  # Move past the last found position

    # Sort keywords based on their position in the text
    keyword_positions.sort(key=lambda x: x[0])
    # Tokenize the text with SpaCy
    doc = nlp(text)
    token_arr = [i for i in doc]
    # Convert positions to token chunks
    token_chunks = []
    for start, end in keyword_positions:
        # Find the start and end tokens for the position
        start_token = None
        end_token = None
        for token in doc:
            if start <= token.idx < end:
                if start_token is None:
                    start_token = token
                end_token = token

        if start_token and end_token:
            # Extract the chunk of tokens
            chunk = doc[start_token.i : end_token.i + 1]
            token_chunks.append(chunk)

    # Merge chunks if needed
    (merged_chunks, merged_count, no_merge_penalty_dict) = merge_chunks(
        token_chunks, doc, max_length
    )
    current_merge_iteration = 0
    interations_run = False
    while not interations_run or (
        current_merge_iteration < max_merge_iterations and merged_count > 0
    ):
        (merged_chunks, merged_count, no_merge_penalty_dict) = merge_chunks(
            merged_chunks, doc, max_length, no_merge_penalty_dict
        )
        current_merge_iteration += 1
        interations_run = True

    output = [i.text for i in merged_chunks]

    return output
