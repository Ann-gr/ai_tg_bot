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