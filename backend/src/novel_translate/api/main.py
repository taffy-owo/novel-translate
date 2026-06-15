from fastapi import APIRouter, FastAPI

app = FastAPI(title="novel-translate")

api_v1_router = APIRouter(prefix="/api/v1")
app.include_router(api_v1_router)


@app.get("/health")
async def read_health() -> dict[str, str]:
    return {"status": "ok"}
