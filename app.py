# app.py
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import spacy
import os

import spacy.tokens

load_dotenv()

max_connect = 5
max_chunk_len = 24  # approximately the max chunk length of each highlight

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")


@app.route("/", methods=["GET"])
def hello():
    return "Hello"


@app.route("/highlight", methods=["POST"])
def highlight():
    data = request.json
    text = data.get("text", "")

    # Replace with your actual text processing logic
    highlighted_words = process_text(text)

    return jsonify({"highlightedWords": highlighted_words})


def process_text(text: str):
    # Example text processing (replace with your ML logic)
    cleaned_text = " ".join(text.split())
    return extract_and_merge(cleaned_text)


def is_unigram(text):
    return len(text.split()) == 1


def is_connector_token(token: spacy.tokens.Token):
    if token.pos_ == "CCONJ":
        return True
    if token.text == "-":
        return True
    return False


def is_chunk_connector_token(token: spacy.tokens.Token):
    if token.pos_ in {"CCONJ", "ADP"}:
        return True
    if token.text == "-":
        return True
    return False


def is_passive_verb(token):
    # Check if the token is a verb
    if token.pos_ != "VERB":
        return False

    # Passive voice in English often involves:
    # - A verb with a passive voice dependency tag
    # - The token having an auxiliary verb (like "be") and a past participle
    if token.dep_ in {"nsubjpass", "agent"}:
        return True

    # Additional checks for complex passive structures
    # Look for auxiliary verbs or particles indicating passive construction
    if token.dep_ == "auxpass" or token.dep_ == "xcomp":
        return True
    if token.tag_ == "VBN":
        return True
    return False


# def extract_and_merge(text: str):
#     doc = nlp(text)
#     merged_list = []
#     noun_chunks = [
#         i
#         for i in doc.noun_chunks
#         if not (is_unigram(i.text) and doc[i.start].pos_ == "PRON")
#     ]
#     noun_chunks_dict = {chunk.start: chunk for chunk in noun_chunks}

#     doc_arr = [i for i in doc]

#     print(noun_chunks_dict)
#     i = 0
#     while i < len(doc):
#         token = doc[i]
#         if i in noun_chunks_dict:
#             if not (is_unigram(noun_chunks_dict[i].text) and doc[i].pos_ != "NOUN"):
#                 chunk_text = noun_chunks_dict[i].text
#                 i += len(noun_chunks_dict[i])
#                 connect_count = 0
#                 while (
#                     i < len(doc)
#                     and connect_count < max_connect
#                     and len(chunk_text) < max_chunk_len
#                 ):
#                     if doc[i].pos_ in {"ADP", "CCONJ"}:
#                         if i + 1 in noun_chunks_dict:
#                             chunk_text += " " + " ".join(
#                                 [
#                                     doc[i].text,
#                                     noun_chunks_dict[i + 1].text,
#                                 ]
#                             )
#                             i += 1 + len(noun_chunks_dict[i + 1])
#                             connect_count += 1
#                         elif doc[i + 1].pos_ in {"NOUN", "NUM"}:
#                             chunk_text += " " + " ".join(
#                                 [
#                                     doc[i].text,
#                                     doc[i + 1].text,
#                                 ]
#                             )
#                             i += 2
#                             connect_count += 1
#                         else:
#                             break
#                     elif doc[i].pos_ in {"SYM"}:
#                         if doc[i + 1].pos_ in {"NOUN", "NUM", "ADJ", "ADV"}:
#                             chunk_text += "" + "".join(
#                                 [
#                                     doc[i].text,
#                                     doc[i + 1].text,
#                                 ]
#                             )
#                             i += 2
#                             connect_count += 1
#                         else:
#                             break
#                     elif doc[i].pos_ in {"NOUN", "NUM", "ADJ", "ADV"}:
#                         chunk_text += " " + doc[i].text
#                         print(chunk_text)
#                         print(len(chunk_text))
#                         i += 1
#                         connect_count += 1

#                     else:
#                         break
#                 if not is_unigram(chunk_text):
#                     merged_list.append(chunk_text)
#             else:
#                 i += 1
#         elif (token.pos_ == "VERB" and token.lemma_ not in {"be", "have"}) or (
#             token.pos_ == "ADJ"
#         ):
#             verb_phrase = token.text
#             i += 1
#             connect_count = 0
#             while (
#                 i < len(doc) - 1
#                 and connect_count < max_connect
#                 and len(verb_phrase) < max_chunk_len
#             ):
#                 if i in noun_chunks_dict:
#                     verb_phrase += " " + noun_chunks_dict[i].text
#                     i += len(noun_chunks_dict[i])
#                     connect_count += 1
#                 elif doc[i].pos_ in {"PART"}:
#                     if i + 1 in noun_chunks_dict:
#                         verb_phrase += " " + " ".join(
#                             [doc[i].text, noun_chunks_dict[i + 1].text]
#                         )
#                         i += 1 + len(noun_chunks_dict[i + 1])
#                         connect_count += 1
#                     elif i + 1 < len(doc) and doc[i + 1].pos_ in {"VERB", "NOUN"}:
#                         verb_phrase += " " + " ".join([doc[i].text, doc[i + 1].text])
#                         i += 2
#                         connect_count += 1
#                     else:
#                         break
#                 elif doc[i].pos_ in {"SYM"}:
#                     if i + 1 in noun_chunks_dict:
#                         verb_phrase += "" + "".join(
#                             [doc[i].text, noun_chunks_dict[i + 1].text]
#                         )
#                         i += 1 + len(noun_chunks_dict[i + 1])
#                         connect_count += 1
#                     elif i + 1 < len(doc) and doc[i + 1].pos_ in {"NOUN", "NUM"}:
#                         verb_phrase += "" + "".join([doc[i].text, doc[i + 1].text])
#                         i += 2
#                         connect_count += 1
#                     else:
#                         break
#                 elif doc[i].pos_ in {"ADJ", "ADV"}:
#                     verb_phrase += " " + doc[i].text
#                     i += 1
#                     connect_count += 1
#                 elif doc[i].pos_ in {"NOUN", "NUM"}:
#                     verb_phrase += " " + doc[i].text
#                     i += 1
#                     connect_count += 1
#                 else:
#                     break
#             if not is_unigram(verb_phrase):
#                 merged_list.append(verb_phrase)
#         else:
#             i += 1


#     output = [i for i in merged_list]
#     print(output)
#     return output
# def extract_and_merge(text: str):
#     doc = nlp(text)
#     merged_list = []
#     noun_chunks = [
#         i
#         for i in doc.noun_chunks
#         if not (is_unigram(i.text) and doc[i.start].pos_ == "PRON")
#     ]
#     noun_chunks_dict = {chunk.start: chunk for chunk in noun_chunks}

#     print(noun_chunks_dict)
#     doc_arr = [i for i in doc]
#     i = 0
#     while i < len(doc):
#         token = doc[i]
#         # determine highlight by expanding from noun_chunks_dict
#         if i in noun_chunks_dict:
#             if not (is_unigram(noun_chunks_dict[i].text) and doc[i].pos_ in {"DET"}):
#                 noun_chunk = noun_chunks_dict[i]
#                 i += len(noun_chunk)
#                 if noun_chunk[0].pos_ in {"DET"} and len(noun_chunk) > 2:
#                     noun_chunk = noun_chunk[1:]
#                 chunk_text = noun_chunk.text + noun_chunk[-1].whitespace_
#                 connect_count = 0
#                 while (
#                     i < len(doc)
#                     and connect_count < max_connect
#                     and len(chunk_text) < max_chunk_len
#                 ):
#                     if doc[i].pos_ in {"ADP", "CCONJ"}:
#                         if i + 1 in noun_chunks_dict and noun_chunks_dict[i + 1][
#                             0
#                         ].pos_ not in {"DET"}:
#                             chunk_text += (
#                                 doc[i].text
#                                 + doc[i].whitespace_
#                                 + noun_chunks_dict[i + 1].text
#                                 + noun_chunks_dict[i + 1][-1].whitespace_
#                             )
#                             i += 1 + len(noun_chunks_dict[i + 1])
#                             connect_count += 1
#                         elif i + 1 < len(doc) and doc[i + 1].pos_ in {
#                             "NOUN",
#                             "NUM",
#                             "PRON",
#                         }:
#                             chunk_text += (
#                                 doc[i].text
#                                 + doc[i].whitespace_
#                                 + doc[i + 1].text
#                                 + doc[i + 1].whitespace_
#                             )
#                             i += 2
#                             connect_count += 1
#                         else:
#                             break
#                     elif doc[i].pos_ in {"SYM", "PUNCT"} and doc[i].text in {
#                         "-",
#                         ",",
#                     }:
#                         if (
#                             i + 1 < len(doc)
#                             and doc[i + 1].pos_
#                             in {
#                                 "NOUN",
#                                 "NUM",
#                                 "ADJ",
#                             }
#                             and i + 1 not in noun_chunks_dict
#                         ):
#                             chunk_text += (
#                                 doc[i].text
#                                 + doc[i].whitespace_
#                                 + doc[i + 1].text
#                                 + doc[i + 1].whitespace_
#                             )
#                             i += 2
#                             connect_count += 1
#                         else:
#                             break
#                     elif (
#                         doc[i].pos_
#                         in {
#                             "NOUN",
#                             "NUM",
#                             "ADJ",
#                         }
#                         and i not in noun_chunks_dict
#                     ):
#                         chunk_text += doc[i].text + doc[i].whitespace_
#                         print(chunk_text)
#                         print(len(chunk_text))
#                         i += 1
#                         connect_count += 1

#                     else:
#                         break
#                 merged_list.append(chunk_text.strip())
#             else:
#                 i += 1
#         elif (token.pos_ == "VERB" and token.lemma_ not in {"be", "have"}) or (
#             token.pos_ == "ADJ" or token.pos_ == "ADV"
#         ):
#             should_append = is_passive_verb(token) or token.pos_ == "ADJ"
#             verb_phrase = token.text + token.whitespace_
#             i += 1
#             connect_count = 0
#             while (
#                 i < len(doc)
#                 and connect_count < max_connect
#                 and len(verb_phrase) < max_chunk_len
#             ):
#                 if i in noun_chunks_dict and noun_chunks_dict[i][0].pos_ != "DET":
#                     verb_phrase += (
#                         noun_chunks_dict[i].text + noun_chunks_dict[i].root.whitespace_
#                     )
#                     i += len(noun_chunks_dict[i])
#                     connect_count += 1
#                 elif doc[i].pos_ in {"PART", "ADP"}:
#                     if (
#                         i + 1 < len(doc)
#                         and i + 1 in noun_chunks_dict
#                         and noun_chunks_dict[i + 1][0].pos_ != "DET"
#                     ):
#                         verb_phrase += (
#                             doc[i].text
#                             + doc[i].whitespace_
#                             + noun_chunks_dict[i + 1].text
#                             + noun_chunks_dict[i + 1][-1].whitespace_
#                         )
#                         i += 1 + len(noun_chunks_dict[i + 1])
#                         connect_count += 1
#                     elif i + 1 < len(doc) and doc[i + 1].pos_ in {
#                         "VERB",
#                         "NOUN",
#                         "PRON",
#                     }:
#                         verb_phrase += (
#                             doc[i].text
#                             + doc[i].whitespace_
#                             + doc[i + 1].text
#                             + doc[i + 1].whitespace_
#                         )
#                         i += 2
#                         connect_count += 1
#                     else:
#                         break
#                 elif doc[i].pos_ in {"SYM", "PUNCT"} and doc[i].text in {
#                     "-",
#                     ",",
#                 }:
#                     if (
#                         i + 1 < len(doc)
#                         and doc[i + 1].pos_
#                         in {
#                             "NOUN",
#                             "NUM",
#                             "NUM",
#                         }
#                         and i + 1 not in noun_chunks_dict
#                     ):
#                         verb_phrase += (
#                             doc[i].text
#                             + doc[i].whitespace_
#                             + doc[i + 1].text
#                             + doc[i + 1].whitespace_
#                         )
#                         i += 2
#                         connect_count += 1
#                     else:
#                         break
#                 elif (
#                     doc[i].pos_
#                     in {
#                         "ADJ",
#                         "ADV",
#                         "ADP",
#                         "VERB",
#                         "NOUN",
#                         "NUM",
#                         "PRON",
#                     }
#                     and i not in noun_chunks_dict
#                 ):
#                     verb_phrase += doc[i].text + doc[i].whitespace_
#                     i += 1
#                     connect_count += 1

#                 else:
#                     break
#             if should_append or not is_unigram(verb_phrase.strip()):
#                 merged_list.append(verb_phrase.strip())
#         else:
#             i += 1

#     output = [i for i in merged_list]
#     print(output)
#     return output


def should_not_start_or_end_chunk_with_token(token: spacy.tokens.Token):
    if token.pos_ in {"ADP", "DET", "CCONJ", "PUNCT", "PART"}:
        return True
    return False


def should_merge_into_noun_chunk(token: spacy.tokens.Token):
    if token.pos_ in {"ADJ", "NOUN", "NUM", "DET", "ADP", "PART"}:
        return True
    if is_passive_verb(token):
        return True
    if is_connector_token(token):
        return True
    return False


def expand_noun_chunk(
    chunk: spacy.tokens.Span,
    doc: spacy.tokens.Doc,
    prev_chunk: spacy.tokens.Span,
    next_chunk: spacy.tokens.Span,
    token_arr,
):
    backward_limit = 5
    forward_limit = 5
    backward_step = 0
    forward_step = 0
    start = chunk.start
    end = chunk.end - 1

    # Expand to the left
    while (
        start > 0
        and backward_step < backward_limit
        and should_merge_into_noun_chunk(doc[start - 1])
    ):
        # Stop expanding if it hits the end of the previous chunk
        if prev_chunk and start <= prev_chunk.end:
            break
        start -= 1
        backward_step += 1

    # Expand to the right
    while (
        end < len(doc) - 1
        and forward_step < forward_limit
        and should_merge_into_noun_chunk(doc[end + 1])
    ):
        # Stop expanding if it hits the start of the next chunk
        if next_chunk and end >= next_chunk.start - 1:
            break
        end += 1
        forward_step += 1

    # while should_not_start_or_end_chunk_with_token(doc[end]) and start < end - 1:
    #     print("skip", doc[end])
    #     end -= 1

    # while should_not_start_or_end_chunk_with_token(doc[start]) and start < end - 1:
    #     start += 1

    return doc[start : end + 1]


def has_no_important(tokens: list):
    return not any(
        token.pos_ in {"ADJ", "NOUN", "NUM", "PROPN", "PRON"} for token in tokens
    )


def truncate_chunk(chunk: spacy.tokens.Span, doc: spacy.tokens.Doc):
    start = chunk.start
    end = chunk.end - 1
    truncated_score = 0

    while start < end - 1 and (
        should_not_start_or_end_chunk_with_token(doc[end])
        or has_no_important(doc[end - 2 : end + 1])
    ):
        print("skip", doc[end])
        end -= 1
        truncated_score += 1

    while start < end - 1 and (
        should_not_start_or_end_chunk_with_token(doc[start])
        or has_no_important(doc[start : start + 3])
    ):
        start += 1
        truncated_score += 1

    return (doc[start : end + 1], truncated_score)


def is_connected(
    chunk: spacy.tokens.Span, next_chunk: spacy.tokens.Span, doc: spacy.tokens.Doc
):
    if chunk.end == next_chunk.start:
        return True
    token_in_betweens = doc[chunk.end : next_chunk.start]
    if all(
        token.pos_ in {"ADP", "CCONJ"} or token.text in {"-"}
        for token in token_in_betweens
    ):
        return True
    return False


def merge_chunks(chunk_list: list, doc: spacy.tokens.Doc):
    merged_chunks = []
    merge_index = 0
    merged_count = 0
    while merge_index < len(chunk_list):
        chunk = chunk_list[merge_index]

        if merge_index < len(chunk_list) - 1:
            next_chunk = chunk_list[merge_index + 1]

            # Check if chunks are consecutive
            if (
                len(chunk) < 6
                and len(next_chunk) < 6
                and is_connected(chunk, next_chunk, doc)
            ):

                # Merge chunks
                merged_chunk = doc[chunk.start : next_chunk.end]
                merged_chunks.append(merged_chunk)
                merge_index += 2  # Skip the next chunk since it's merged
                merged_count += 1
                continue

        # If no merging, add the current chunk
        merged_chunks.append(chunk)
        merge_index += 1
    return (merged_chunks, merged_count)


def truncate_chunks(chunk_list: list, doc: spacy.tokens.Doc):
    truncated_chunks = []
    total_truncated_score = 0
    for chunk in chunk_list:
        (truncated_chunk, truncate_score) = truncate_chunk(chunk, doc)
        total_truncated_score += truncate_score
        truncated_chunks.append((truncated_chunk, truncate_score))
    return (truncated_chunks, total_truncated_score)


def expand_chunks(
    chunk_list: list, reference_list: list, doc: spacy.tokens.Doc, token_arr: list
):
    expanded_chunks_dict = {}
    expanded_chunks = []

    for chunk in chunk_list:
        # Determine the index of the chunk in the reference list by comparing start tokens
        match_index_in_reference_list = next(
            (
                i
                for i, ref_chunk in enumerate(reference_list)
                if ref_chunk.start == chunk.start
            ),
            None,
        )

        if match_index_in_reference_list is None:
            continue  # If no match is found, skip this chunk

        prev_chunk = (
            None
            if match_index_in_reference_list == 0
            else reference_list[match_index_in_reference_list - 1]
        )
        if prev_chunk and prev_chunk.start in expanded_chunks_dict:
            prev_chunk = expanded_chunks_dict[prev_chunk.start]

        next_chunk = (
            None
            if match_index_in_reference_list == len(reference_list) - 1
            else reference_list[match_index_in_reference_list + 1]
        )
        if next_chunk and next_chunk.start in expanded_chunks_dict:
            next_chunk = expanded_chunks_dict[next_chunk.start]

        expanded_chunk = expand_noun_chunk(
            chunk, doc, prev_chunk, next_chunk, token_arr
        )
        expanded_chunks_dict[chunk.start] = expanded_chunk
        expanded_chunks.append(expanded_chunk)

    return expanded_chunks


def extract_and_merge(text: str):
    doc = nlp(text)
    token_arr = [token for token in doc]
    # Extract noun chunks and entities
    noun_chunks = [chunk for chunk in doc.noun_chunks]
    entities = [ent for ent in doc.ents]

    # Combine entities and noun chunks, prioritizing entities
    combined_chunks = noun_chunks.copy()  # Start with entities
    noun_chunk_indices = set()  # Track indices covered by entities

    # Mark indices covered by entities
    for ent in noun_chunks:
        noun_chunk_indices.update(range(ent.start, ent.end))

    # Add noun chunks if they do not overlap with any entity indices
    for ent in entities:
        if not any(i in noun_chunk_indices for i in range(ent.start, ent.end)):
            combined_chunks.append(ent)

    combined_chunks.sort(key=lambda x: x.start)
    max_iterations = 3
    i = 0
    history = []

    filtered_chunks = [
        chunk
        for chunk in combined_chunks
        if (len(chunk) > 1 or chunk[0].pos_ in {"NOUN", "NUM", "PROPN"})
    ]

    cloned = filtered_chunks.copy()
    while i < max_iterations:
        i += 1
        print(f"Iteration {i}")
        # Make a clone of noun chunks
        expanded_chunks = expand_chunks(cloned, filtered_chunks, doc, token_arr)

        # Pass the expanded chunks to truncate_chunks
        truncated_chunks, total_truncated_score = truncate_chunks(expanded_chunks, doc)

        if i >= 2 and total_truncated_score <= history[len(history) - 1][0]:
            break
        # Record the truncated chunks with their total truncate score
        history.append(
            (
                total_truncated_score,
                truncated_chunks,
            )
        )

        if i >= 1:
            sorted_truncated_chunks_with_index = sorted(
                [(chunk, index) for index, chunk in enumerate(truncated_chunks)],
                key=lambda x: x[0][1],
            )

            new_cloned = [
                cloned[index] for (_, index) in sorted_truncated_chunks_with_index
            ]

            cloned = new_cloned
    if len(history) == 0:
        return []

    # Merge chunks if needed
    (merged_chunks, merged_count) = merge_chunks(
        sorted(
            [chunk for chunk, _ in history[len(history) - 1][1]], key=lambda x: x.start
        ),
        doc,
    )
    while merged_count > 0:
        (merged_chunks, merged_count) = merge_chunks(merged_chunks, doc)

    output = [i.text for i in merged_chunks]

    print(output)
    return output


if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    print("Running with env of ", env)
    ssl_context = (
        ("./localhost.pem", "./localhost-key.pem") if env == "development" else None
    )
    app.run(debug=True, port=5000, ssl_context=ssl_context)
