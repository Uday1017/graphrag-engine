from dataclasses import dataclass

@dataclass
class Chunk:
    text: str
    metadata: dict

def chunk_text(
    text: str,
    metadata: dict,
    chunk_size: int = 512,
    overlap: int = 64,
) -> list[Chunk]:
    words = text.split()
    chunks = []
    start = 0
    idx = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_text_str = " ".join(words[start:end])
        chunks.append(Chunk(
            text=chunk_text_str,
            metadata={**metadata, "chunk_index": idx}
        ))
        idx += 1
        start += chunk_size - overlap

    return chunks
