# app.py
from flask import Flask, request, jsonify, make_response
import spacy

# from flask_cors import CORS

app = Flask(__name__)
# CORS(app)  # This will enable CORS for all domains and all routes

nlp = spacy.load("en_core_web_sm")


@app.route("/", methods=["GET"])
def hello():
    return "Hello"


@app.route("/highlight", methods=["POST"])
def highlight():
    # if request.method == "OPTIONS":  # CORS preflight
    #     return _build_cors_preflight_response()

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


def extract_and_merge(text: str):
    doc = nlp(
        text,
    )
    merged_list = []
    noun_chunks = [
        i
        for i in doc.noun_chunks
        if not (is_unigram(i.text) and doc[i.start].pos_ == "PRON")
    ]
    noun_chunks_dict = {chunk.start: chunk for chunk in noun_chunks}

    doc_arr = [i for i in doc]

    print(noun_chunks_dict)
    i = 0
    while i < len(doc):
        token = doc[i]
        if i in noun_chunks_dict:
            if not (is_unigram(noun_chunks_dict[i].text) and doc[i].pos_ != "NOUN"):
                chunk_text = noun_chunks_dict[i].text
                next_token_idx = i + len(noun_chunks_dict[i])
                i = next_token_idx

                while next_token_idx < len(doc):
                    if (
                        doc[next_token_idx].pos_
                        in {
                            "ADP",
                            "PART",
                        }
                        and next_token_idx + 1 in noun_chunks_dict
                    ):
                        chunk_text += " " + " ".join(
                            [
                                doc[next_token_idx].text,
                                noun_chunks_dict[next_token_idx + 1].text,
                            ]
                        )
                        # i += 1 + len(noun_chunks_dict[next_token_idx + 1])

                        next_token_idx += 1 + len(noun_chunks_dict[next_token_idx + 1])
                        i = next_token_idx - 1
                    else:
                        break
                merged_list.append(chunk_text)
        elif token.pos_ in {
            "VERB",
            "AUX",
            "ADV",
            "ADJ",
            "PART",
        }:
            verb_phrase = token.text
            if token.lemma_ != "be" or token.dep_ == "neg":
                while i + 1 <= len(doc) - 1:
                    # Check if the next token is a preposition or particle or noun chunk starts right after the verb
                    if i + 1 in noun_chunks_dict:
                        verb_phrase += " " + noun_chunks_dict[i + 1].text
                        i += len(noun_chunks_dict[i + 1])
                    elif doc[i + 1].pos_ in {"PART"}:
                        if i + 2 in noun_chunks_dict:
                            verb_phrase += " " + " ".join(
                                [doc[i + 1].text, noun_chunks_dict[i + 2].text]
                            )
                            i += 1 + len(noun_chunks_dict[i + 2])
                        elif i + 2 < len(doc) and doc[i + 2].pos_ == "VERB":
                            verb_phrase += " " + " ".join(
                                [doc[i + 1].text, doc[i + 2].text]
                            )
                            i += 2
                        else:
                            i += 1
                    elif doc[i + 1].pos_ in {"ADJ", "VERB"}:
                        verb_phrase += " " + doc[i + 1].text
                        i += 1
                    else:
                        break
                if (
                    not is_unigram(verb_phrase)
                    or is_passive_verb(token)
                    or token.pos_ == "ADJ"
                ):
                    merged_list.append(verb_phrase)

        i += 1

    output = [i for i in merged_list]
    print(output)
    return output


# def _build_cors_preflight_response():
#     response = make_response()
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     response.headers.add("Access-Control-Allow-Headers", "*")
#     response.headers.add("Access-Control-Allow-Methods", "*")
#     return response


# def _corsify_actual_response(response):
#     response.headers.add("Access-Control-Allow-Origin", "*")
#     return response


if __name__ == "__main__":
    app.run(
        debug=True, port=5000, ssl_context=("./localhost.pem", "./localhost-key.pem")
    )
