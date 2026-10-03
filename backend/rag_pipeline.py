
import os
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv()

import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from docx import Document as DocxDocument
import markdown as md

SUPPORTED_EXTS = {".pdf", ".docx", ".txt", ".md"}
TOKENIZER_SENTINEL_MAX_LENGTH = 1_000_000

def read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            text_parts = []
            reader = PdfReader(path)
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)
        elif ext == ".docx":
            doc = DocxDocument(path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext == ".md":
            # Convert markdown to plain text by stripping HTML tags after conversion
            html = md.markdown(open(path, "r", encoding="utf-8", errors="ignore").read())
            # naive strip of tags
            import re
            return re.sub("<[^<]+?>", "", html)
        else:
            return open(path, "r", encoding="utf-8", errors="ignore").read()
    except Exception as e:
        return ""

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 0) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    if chunk_size <= 0:
        chunk_size = 900
    if overlap < 0:
        overlap = 0
    if overlap >= chunk_size:
        overlap = 0
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        # move window
        step = chunk_size - overlap
        if step <= 0:
            step = chunk_size
        start += step
        # guard to avoid infinite loop on tiny texts
        if start == 0:
            break
    return chunks

@dataclass
class RetrievedChunk:
    doc_id: str
    score: float
    preview: str
    text: str

class EmbeddingTokenLimitError(ValueError):
    pass

class RAGEngine:
    def __init__(self, persist_dir: str = "storage",
                 collection: str = "legal_docs",
                 embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        # Persistent client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(collection)
        self.embedder = SentenceTransformer(embed_model)
        self.embedding_model_name = embed_model
        self.embedding_token_limit = self._detect_embedding_token_limit()

    def use_collection(self, name: str):
        self.collection = self.client.get_or_create_collection(name)

    def _detect_embedding_token_limit(self) -> int:
        limits = []

        get_max_seq_length = getattr(self.embedder, "get_max_seq_length", None)
        if callable(get_max_seq_length):
            max_seq_length = get_max_seq_length()
            if isinstance(max_seq_length, int) and max_seq_length > 0:
                limits.append(max_seq_length)

        max_seq_length = getattr(self.embedder, "max_seq_length", None)
        if isinstance(max_seq_length, int) and max_seq_length > 0:
            limits.append(max_seq_length)

        tokenizer = getattr(self.embedder, "tokenizer", None)
        tokenizer_max_length = getattr(tokenizer, "model_max_length", None)
        if (
            isinstance(tokenizer_max_length, int)
            and 0 < tokenizer_max_length < TOKENIZER_SENTINEL_MAX_LENGTH
        ):
            limits.append(tokenizer_max_length)

        if not limits:
            raise RuntimeError(
                f"Could not determine token limit for embedding model {self.embedding_model_name}"
            )

        return min(limits)

    def _get_embedding_tokenizer(self):
        tokenizer = getattr(self.embedder, "tokenizer", None)
        if tokenizer is None:
            raise RuntimeError(
                f"Could not find tokenizer for embedding model {self.embedding_model_name}"
            )
        return tokenizer

    def _count_embedding_tokens(self, texts: List[str]) -> List[int]:
        tokenizer = self._get_embedding_tokenizer()
        encoded = tokenizer(
            [text or "" for text in texts],
            add_special_tokens=True,
            truncation=False,
            padding=False,
        )
        return [len(token_ids) for token_ids in encoded["input_ids"]]

    def _validate_embedding_token_limits(self, texts: List[str], context: str) -> None:
        token_counts = self._count_embedding_tokens(texts)
        for index, token_count in enumerate(token_counts):
            if token_count > self.embedding_token_limit:
                raise EmbeddingTokenLimitError(
                    f"{context} item {index} has {token_count} tokens, "
                    f"which exceeds the {self.embedding_token_limit}-token limit for "
                    f"embedding model {self.embedding_model_name}. Reduce chunk_size or input length."
                )

    def ingest_directory(self, directory: str,
                         chunk_size: int = 900,
                         overlap: int = 150,
                         default_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        default_metadata = default_metadata or {}
        total_files = 0
        total_chunks = 0
        ingested_files = 0

        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if not os.path.isfile(file_path):
                continue
            ext = os.path.splitext(file_name)[1].lower()
            if ext not in SUPPORTED_EXTS:
                continue

            total_files += 1
            text = read_file(file_path)
            chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
            if not chunks:
                # Skip empty/invalid files
                continue

            # Prepare documents/metadata/ids
            documents = chunks
            metadatas = []
            for i, _ in enumerate(chunks):
                meta = {"source": file_name, "doc_id": file_path, "chunk_index": i}
                meta.update(default_metadata)
                metadatas.append(meta)
            ids = [f"{file_name}-{i}-{uuid.uuid4()}" for i in range(len(chunks))]

            self._validate_embedding_token_limits(documents, f"File {file_name}")

            # Compute embeddings
            #embeddings = self.embedder.encode(documents, convert_to_numpy=True).tolist()
            # Compute embeddings
            embeddings = self.embedder.encode(documents, convert_to_numpy=True)

            # Ensure it's always 2D (n_chunks x embedding_dim)
            if embeddings.ndim == 1:
                embeddings = embeddings.reshape(1, -1)

            embeddings = [list(map(float, emb)) for emb in embeddings]
            # Sanity checks
            assert len(documents) == len(metadatas) == len(ids) == len(embeddings), \
                f"Length mismatch: docs={len(documents)}, metas={len(metadatas)}, ids={len(ids)}, embs={len(embeddings)}"

            # Ensure embeddings are 2D
            if isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], float):
                embeddings = [embeddings]

            # print("Sample doc:", type(documents[0]), documents[0][:80] if documents else None)
            # print("Sample meta:", type(metadatas[0]), metadatas[0] if metadatas else None)
            # print("Sample id:", type(ids[0]), ids[0] if ids else None)
            # print("Sample embedding:", type(embeddings[0]), type(embeddings[0][0]), len(embeddings[0]) if embeddings else None)
            # Upsert to allow re-ingestion while keeping unique IDs per run
            self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
            )

            total_chunks += len(chunks)
            ingested_files += 1

        return {
            "files_scanned": total_files,
            "files_ingested": ingested_files,
            "chunks_added": total_chunks
        }

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievedChunk]:
        self._validate_embedding_token_limits([query], "Query")
        qemb = self.embedder.encode([query], convert_to_numpy=True)[0].tolist()
        res = self.collection.query(query_embeddings=[qemb], n_results=top_k)
        out: List[RetrievedChunk] = []
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        for doc, meta, dist in zip(docs, metas, dists):
            out.append(RetrievedChunk(
                doc_id=str(meta.get("doc_id", "")),
                score=float(dist),
                preview=(doc[:300] + ("…" if len(doc) > 300 else "")),
                text=doc
            ))
        return out

    def build_prompt(self, question: str, retrieved: List[RetrievedChunk]) -> str:
        context = "\n\n".join([f"[{i+1}] {rc.text}" for i, rc in enumerate(retrieved)])
        prompt = f"""You are an assistant for a legal firm. Answer the question using ONLY the context.
If the answer is not in the context, say you don't know.

Question:
{question}

Context:
{context}

Provide a concise answer with bullet points if appropriate, and cite chunk numbers like [1], [2].
"""
        return prompt
