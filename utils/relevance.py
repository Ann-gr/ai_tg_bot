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