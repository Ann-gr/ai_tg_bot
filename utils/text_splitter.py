def split_text(text: str, chunk_size: int = 500):
    chunks = []
    current = ""

    for paragraph in text.split("\n"):
        if len(current) + len(paragraph) < chunk_size:
            current += paragraph + "\n"
        else:
            chunks.append(current.strip())
            current = paragraph + "\n"

    if current:
        chunks.append(current.strip())

    return chunks