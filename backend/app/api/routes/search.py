from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class SearchQuery(BaseModel):
    q: str


@router.post("/search")
async def search(query: SearchQuery):
    # Placeholder implementation: real implementation would query metadata/vector store
    return {"results": []}
