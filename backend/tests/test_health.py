from httpx import ASGITransport, AsyncClient

from novel_translate.api.main import app


async def test_health_reports_ok() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
