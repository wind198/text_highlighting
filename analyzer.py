import spacy
from helpers import truncate_chunks, expand_chunks, merge_chunks
import spacy.tokens

nlp = spacy.load("en_core_web_sm")


def extract_keywords(text: str):
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

    return output
