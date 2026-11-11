"""
ChromaDB Vector Store Service for Semantic Search and Evidence Retrieval.
"""
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class ChromaService:
    """
    Manages persistent vector embeddings in ChromaDB with strict vendor isolation.
    """

    COLLECTION_NAME = "vendor_documents"

    def __init__(self, persist_directory: Optional[str] = None, client: Optional[Any] = None):
        """
        Initializes persistent or ephemeral ChromaDB client and gets/creates collection.
        """
        if client is not None:
            self.client = client
        else:
            persist_dir = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
            self.client = chromadb.PersistentClient(path=persist_dir)

        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, vendor_id: int, chunks: List[Any]) -> int:
        """
        Upserts chunk embeddings into ChromaDB with metadata.
        Accepts list of DocumentChunk models or dicts.
        """
        if not chunks:
            return 0

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for chk in chunks:
            # Handle both ORM DocumentChunk instances and dicts
            if hasattr(chk, "chunk_id"):
                c_id = str(chk.chunk_id)
                doc_id = str(chk.document_id)
                v_id = int(chk.vendor_id)
                filename = str(chk.original_filename or "")
                page = int(chk.page_number or 1)
                section = str(chk.section or "General")
                index = int(chk.chunk_index or 0)
                text = str(chk.chunk_text or "")
            else:
                c_id = str(chk.get("chunk_id", ""))
                doc_id = str(chk.get("document_id", ""))
                v_id = int(chk.get("vendor_id", vendor_id))
                filename = str(chk.get("filename", chk.get("original_filename", "")))
                page = int(chk.get("page_number", 1))
                section = str(chk.get("section", "General"))
                index = int(chk.get("chunk_index", 0))
                text = str(chk.get("text", chk.get("chunk_text", "")))

            if not text.strip():
                continue

            ids.append(c_id)
            documents.append(text)
            metadatas.append({
                "vendor_id": v_id,
                "document_id": doc_id,
                "filename": filename,
                "page_number": page,
                "section": section,
                "chunk_index": index,
            })

        if not ids:
            return 0

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        return len(ids)

    def search(self, vendor_id: int, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search strictly filtered by vendor_id.
        Returns top-k matching chunks with similarity distance and metadata.
        """
        if not query or not query.strip():
            return []

        # Check if collection has documents for this vendor
        count_res = self.collection.get(
            where={"vendor_id": int(vendor_id)},
            limit=1
        )
        if not count_res or not count_res.get("ids"):
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"vendor_id": int(vendor_id)},
            include=["documents", "metadatas", "distances"]
        )

        items: List[Dict[str, Any]] = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return []

        ids = results["ids"][0]
        docs = results["documents"][0] if results.get("documents") else []
        metas = results["metadatas"][0] if results.get("metadatas") else []
        dists = results["distances"][0] if results.get("distances") else []

        for i, c_id in enumerate(ids):
            meta = metas[i] if i < len(metas) else {}
            doc_text = docs[i] if i < len(docs) else ""
            dist = float(dists[i]) if i < len(dists) else 0.0

            items.append({
                "chunk_id": c_id,
                "document_id": meta.get("document_id", ""),
                "vendor_id": meta.get("vendor_id", vendor_id),
                "filename": meta.get("filename", ""),
                "page_number": meta.get("page_number", 1),
                "section": meta.get("section", "General"),
                "chunk_index": meta.get("chunk_index", 0),
                "text": doc_text,
                "distance": dist,
            })

        return items

    def delete_document(self, document_id: str) -> int:
        """
        Deletes all chunks belonging to a document.
        """
        res = self.collection.get(
            where={"document_id": str(document_id)}
        )
        ids = res.get("ids", [])
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    def delete_vendor(self, vendor_id: int) -> int:
        """
        Deletes all chunks belonging to a vendor.
        """
        res = self.collection.get(
            where={"vendor_id": int(vendor_id)}
        )
        ids = res.get("ids", [])
        if ids:
            self.collection.delete(ids=ids)
        return len(ids)

    def get_stats(self, vendor_id: int) -> Dict[str, Any]:
        """
        Returns stats for vendor embeddings.
        """
        res = self.collection.get(
            where={"vendor_id": int(vendor_id)}
        )
        count = len(res.get("ids", []))
        return {
            "vendor_id": int(vendor_id),
            "total_chunks": count,
            "collection_name": self.COLLECTION_NAME,
        }

