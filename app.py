# app.py
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import spacy
import os

load_dotenv()

max_connect = 3
max_chunk_len = 18  # approximately the max chunk length of each highlight

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
def extract_and_merge(text: str):
    doc = nlp(text)
    merged_list = []
    noun_chunks = [
        i
        for i in doc.noun_chunks
        if not (is_unigram(i.text) and doc[i.start].pos_ == "PRON")
    ]
    noun_chunks_dict = {chunk.start: chunk for chunk in noun_chunks}

    print(noun_chunks_dict)
    i = 0
    while i < len(doc):
        token = doc[i]
        if i in noun_chunks_dict:
            if not (is_unigram(noun_chunks_dict[i].text) and doc[i].pos_ != "NOUN"):
                chunk_text = (
                    noun_chunks_dict[i].text + noun_chunks_dict[i][-1].whitespace_
                )
                i += len(noun_chunks_dict[i])
                connect_count = 0
                while (
                    i < len(doc)
                    and connect_count < max_connect
                    and len(chunk_text) < max_chunk_len
                ):
                    if doc[i].pos_ in {"ADP", "CCONJ"}:
                        if i + 1 in noun_chunks_dict:
                            chunk_text += (
                                doc[i].text
                                + doc[i].whitespace_
                                + noun_chunks_dict[i + 1].text
                                + noun_chunks_dict[i + 1][-1].whitespace_
                            )
                            i += 1 + len(noun_chunks_dict[i + 1])
                            connect_count += 1
                        elif doc[i + 1].pos_ in {"NOUN", "NUM"}:
                            chunk_text += (
                                doc[i].text
                                + doc[i].whitespace_
                                + doc[i + 1].text
                                + doc[i + 1].whitespace_
                            )
                            i += 2
                            connect_count += 1
                        else:
                            break
                    elif doc[i].pos_ in {"SYM", "PUNCT"}:
                        if doc[i + 1].pos_ in {"NOUN", "NUM", "ADJ", "ADV"}:
                            chunk_text += (
                                doc[i].text
                                + doc[i].whitespace_
                                + doc[i + 1].text
                                + doc[i + 1].whitespace_
                            )
                            i += 2
                            connect_count += 1
                        else:
                            break
                    elif doc[i].pos_ in {"NOUN", "NUM", "ADJ", "ADV"}:
                        chunk_text += doc[i].text + doc[i].whitespace_
                        print(chunk_text)
                        print(len(chunk_text))
                        i += 1
                        connect_count += 1

                    else:
                        break
                if not is_unigram(chunk_text.strip()):
                    merged_list.append(chunk_text.strip())
            else:
                i += 1
        elif (token.pos_ == "VERB" and token.lemma_ not in {"be", "have"}) or (
            token.pos_ == "ADJ" or token.pos_ == "ADV"
        ):
            verb_phrase = token.text + token.whitespace_
            i += 1
            connect_count = 0
            while (
                i < len(doc) - 1
                and connect_count < max_connect
                and len(verb_phrase) < max_chunk_len
            ):
                if i in noun_chunks_dict:
                    verb_phrase += (
                        noun_chunks_dict[i].text + noun_chunks_dict[i].root.whitespace_
                    )
                    i += len(noun_chunks_dict[i])
                    connect_count += 1
                elif doc[i].pos_ in {"PART"}:
                    if i + 1 in noun_chunks_dict:
                        verb_phrase += (
                            doc[i].text
                            + doc[i].whitespace_
                            + noun_chunks_dict[i + 1].text
                            + noun_chunks_dict[i + 1][-1].whitespace_
                        )
                        i += 1 + len(noun_chunks_dict[i + 1])
                        connect_count += 1
                    elif i + 1 < len(doc) and doc[i + 1].pos_ in {"VERB", "NOUN"}:
                        verb_phrase += (
                            doc[i].text
                            + doc[i].whitespace_
                            + doc[i + 1].text
                            + doc[i + 1].whitespace_
                        )
                        i += 2
                        connect_count += 1
                    else:
                        break
                elif doc[i].pos_ in {"SYM", "PUNCT"}:
                    if i + 1 in noun_chunks_dict:
                        verb_phrase += (
                            doc[i].text
                            + noun_chunks_dict[i + 1].text
                            + noun_chunks_dict[i + 1][-1].whitespace_
                        )
                        i += 1 + len(noun_chunks_dict[i + 1])
                        connect_count += 1
                    elif i + 1 < len(doc) and doc[i + 1].pos_ in {"NOUN", "NUM"}:
                        verb_phrase += (
                            doc[i].text
                            + doc[i].whitespace_
                            + doc[i + 1].text
                            + doc[i + 1].whitespace_
                        )
                        i += 2
                        connect_count += 1
                    else:
                        break
                elif doc[i].pos_ in {"ADJ", "ADV"}:
                    verb_phrase += doc[i].text + doc[i].whitespace_
                    i += 1
                    connect_count += 1
                elif doc[i].pos_ in {"NOUN", "NUM"}:
                    verb_phrase += doc[i].text + doc[i].whitespace_
                    i += 1
                    connect_count += 1
                else:
                    break
            if not is_unigram(verb_phrase.strip()):
                merged_list.append(verb_phrase.strip())
        else:
            i += 1

    output = [i for i in merged_list]
    print(output)
    return output


if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    print("Running with env of ", env)
    ssl_context = (
        ("./localhost.pem", "./localhost-key.pem") if env == "development" else None
    )
    app.run(debug=True, port=5000, ssl_context=ssl_context)
