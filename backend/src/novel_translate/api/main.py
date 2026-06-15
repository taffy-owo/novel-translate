from fastapi import APIRouter, FastAPI

from novel_translate.api.v1 import chapters, projects, segments

app = FastAPI(title="novel-translate")

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(projects.router)
api_v1_router.include_router(chapters.router)
api_v1_router.include_router(segments.router)
app.include_router(api_v1_router)


@app.get("/health")
async def read_health() -> dict[str, str]:
    return {"status": "ok"}
