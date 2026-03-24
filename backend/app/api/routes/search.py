from fastapi import APIRouter
from pydantic import BaseModel

from ...services.rag import reindex_all, retrieve_relevant_chunks

router = APIRouter()


class SearchQuery(BaseModel):
    q: str


class IndexRequest(BaseModel):
    docs_dir: str = "/data/docs"


@router.post("/search")
async def search(query: SearchQuery):
    results = retrieve_relevant_chunks(query.q, top_k=5)
    return {"results": results}


@router.post("/index")
async def index_docs(req: IndexRequest):
    result = reindex_all(req.docs_dir)
    return result
