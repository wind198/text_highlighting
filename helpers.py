import spacy
import spacy.tokens


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
        token.pos_
        in {
            "ADP",
            "PART",
            "CCONJ",
        }
        or token.text in {"-"}
        for token in token_in_betweens
    ):
        return True

    even_pos_token = [
        t for (index, t) in enumerate(token_in_betweens) if index % 2 == 0
    ]
    if all(
        token.pos_
        in {
            "CCONJ",
        }
        or token.text in {"-"}
        for token in even_pos_token
    ):
        return True

    return False


def merge_chunks(
    chunk_list: list,
    doc: spacy.tokens.Doc,
    max_length: int,
    no_merge_penalty_dict: dict = {},
):
    if len(chunk_list) < 2:
        return (chunk_list, 0, {})
    # Sort chunks by their penalty factor, and then length (shortest to longest) but maintain original order
    sorted_chunks_with_indices = sorted(
        enumerate(chunk_list),
        key=lambda x: (no_merge_penalty_dict.get(x[1].text, len(x[1]) + 1), len(x[1])),
    )
    merged_chunks = []
    used_indices = set()
    merged_count = 0
    no_merge_penalty_dict = {}  # key is chunk text, value is penalty factor

    for index, chunk in sorted_chunks_with_indices:
        if index in used_indices:
            continue  # Skip already merged chunks

        # Find the next chunk in the original order
        if index < len(chunk_list) - 1:
            next_chunk_index = index + 1

            # Check if next chunk exists and is not already used
            if next_chunk_index in used_indices:
                merged_chunks.append(chunk)
                used_indices.add(index)
                continue
            else:
                next_chunk = chunk_list[next_chunk_index]

                # Check if chunks are consecutive and within max length
                if len(chunk) + len(next_chunk) <= max_length and is_connected(
                    chunk, next_chunk, doc
                ):
                    # Merge chunks
                    merged_chunk = doc[chunk.start : next_chunk.end]
                    merged_chunks.append(merged_chunk)
                    used_indices.add(index)
                    used_indices.add(
                        next_chunk_index
                    )  # Add next_chunk_index to used indices
                    merged_count += 1
                    continue
                else:
                    merged_chunks.append(chunk)
                    used_indices.add(index)
                    no_merge_penalty_dict[chunk.text] = len(chunk) + max_length

        # If no merging, add the current chunk
        else:
            no_merge_penalty_dict[chunk.text] = len(chunk) + max_length
            merged_chunks.append(chunk)
            used_indices.add(index)

        # add penalty factor for this chunk due to no merging

    # Sort merged_chunks by their start position to maintain original order
    merged_chunks = sorted(merged_chunks, key=lambda x: x.start)

    return (merged_chunks, merged_count, no_merge_penalty_dict)


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
