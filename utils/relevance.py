def score_chunk(chunk: str, question: str) -> int:
    score = 0

    q_words = question.lower().split()

    for word in q_words:
        if word in chunk.lower():
            score += 2

    if len(chunk) < 300:
        score += 1

    return score

def get_top_chunks(chunks, question, top_k=3):
    scored = [(c, score_chunk(c, question)) for c in chunks]
    scored.sort(key=lambda x: x[1], reverse=True)

    return [c for c, s in scored[:top_k] if s > 0]

def select_relevant_chunks(chunks, query, top_k=3):
    query_words = set(query.lower().split())

    scored = []

    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        score = len(query_words & chunk_words)
        scored.append((score, chunk))

    # сортируем по релевантности
    scored.sort(reverse=True, key=lambda x: x[0])

    return [chunk for _, chunk in scored[:top_k]]