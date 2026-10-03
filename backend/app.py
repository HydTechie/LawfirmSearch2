
from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os

from rag_pipeline import EmbeddingTokenLimitError, RAGEngine
from llm_providers import OllamaLLM, FallbackExtractiveLLM , LLMResponse

app = FastAPI(title="Legal SLM RAG POC", version="0.2.0")

ENGINE = RAGEngine(persist_dir="storage")

class IngestRequest(BaseModel):
    directory: str = Field(..., description="Directory path to ingest")
    collection: str = Field("legal_docs", description="Chroma collection name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata to add to each chunk")
    chunk_size: int = Field(900, description="Chunk size in characters")
    overlap: int = Field(150, description="Character overlap between chunks")

class QueryRequest(BaseModel):
    question: str
    collection: str = "legal_docs"
    top_k: int = 5
    model: str = Field("phi3:mini", description="Ollama model name, e.g., phi3:mini, mistral, llama3")
    use_llm: bool = True

origins = [
    "http://localhost:3002",
    # you can add more allowed origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # can be ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],        # allow GET, POST, etc.
    allow_headers=["*"],        # allow custom headers
)

@app.get("/health")
def health():
    return {"status":"ok, Phani"}

@app.post("/ingest")
def ingest(req: IngestRequest):
    if not os.path.isdir(req.directory):
        raise HTTPException(status_code=400, detail=f"directory not found: {req.directory}")

    ENGINE.use_collection(req.collection)

    try:
        result = ENGINE.ingest_directory(
            directory=req.directory,
            chunk_size=req.chunk_size,
            overlap=req.overlap,
            default_metadata=req.metadata or {}
        )
    except EmbeddingTokenLimitError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"collection": req.collection, **result}

@app.post("/query")
def query(req: QueryRequest):
    ENGINE.use_collection(req.collection)
    try:
        retrieved = ENGINE.retrieve(req.question, top_k=req.top_k)
    except EmbeddingTokenLimitError as e:
        raise HTTPException(status_code=400, detail=str(e))

    sources = [{"doc_id": r.doc_id, "score": r.score,
                "preview": r.preview} for r in retrieved]

    if not req.use_llm:
        return {"answer": "LLM disabled. Top snippets returned",
                "sources": sources, "used_llm": "none"}

    prompt = ENGINE.build_prompt(req.question, retrieved)

    # Try ollama first, then fallback
    try:
        llm = OllamaLLM(model=req.model)
        out: LLMResponse = llm.generate(prompt)
    except Exception as e:
        fb = FallbackExtractiveLLM()
        out = fb.generate("\n\n".join([s['preview'] for s in sources]))
        out.text += f"\n\n[Note] {e}"

    return {"answer": out.text, "sources": sources, "used_llm": out.provider}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
    print("Super!")
