from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def query_docs():
    return {"message": "Query route working"}