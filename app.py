# app.py
from flask import Flask, request, jsonify
import spacy

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


def extract_and_merge(text: str):
    doc = nlp(text)
    merged_list = []
    noun_chunks = list(doc.noun_chunks)
    noun_chunks_dict = {chunk.start: chunk for chunk in noun_chunks}

    i = 0
    while i < len(doc):
        token = doc[i]
        if token.pos_ == "VERB":
            verb_phrase = token.text
            if i + 1 < len(doc):
                next_token = doc[i + 1]
                # Check if the next token is a preposition or particle or noun chunk starts right after the verb
                if next_token.pos_ in {"ADP", "PART"} or (i + 1 in noun_chunks_dict):
                    if next_token.pos_ in {"ADP", "PART"} and (
                        i + 2 in noun_chunks_dict
                    ):
                        # If there's an ADP or PART followed by a noun chunk, merge them
                        verb_phrase += (
                            " " + next_token.text + " " + noun_chunks_dict[i + 2].text
                        )
                        i += 2  # Skip the ADP/PART and noun chunk
                    elif i + 1 in noun_chunks_dict:
                        # If there's a noun chunk right after the verb, merge them
                        verb_phrase += " " + noun_chunks_dict[i + 1].text
                        i += 1  # Skip the noun chunk
            merged_list.append(verb_phrase)
        if i in noun_chunks_dict and token.pos_ != "VERB":
            merged_list.append(noun_chunks_dict[i].text)
        i += 1

    return [i for i in merged_list if not is_unigram(i)]


if __name__ == "__main__":
    app.run(debug=True, port=5000)
