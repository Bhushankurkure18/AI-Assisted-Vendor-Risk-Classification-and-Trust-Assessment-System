"""
Deduplication and Hashing Handler for Chunks and Documents.
"""
import hashlib
from typing import Set


class DeduplicationHandler:
    """
    Computes SHA-256 digests and detects duplicate chunks across processing runs.
    """

    @staticmethod
    def compute_chunk_hash(text: str) -> str:
        """
        Computes SHA-256 for a chunk's normalized text.
        """
        hasher = hashlib.sha256()
        hasher.update(text.strip().encode("utf-8"))
        return hasher.hexdigest()

    @classmethod
    def filter_duplicate_chunks(cls, chunks: list) -> list:
        """
        Deduplicates a list of chunk dictionaries based on content_hash.
        """
        seen_hashes: Set[str] = set()
        unique_chunks = []
        for chk in chunks:
            h = chk.get("content_hash")
            if h and h not in seen_hashes:
                seen_hashes.add(h)
                unique_chunks.append(chk)
        return unique_chunks

