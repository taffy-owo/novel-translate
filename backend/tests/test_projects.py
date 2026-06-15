from uuid import uuid4

from httpx import AsyncClient


async def test_create_and_read_project(client: AsyncClient) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={"name": "第一卷", "provider_config": {"kind": "openai_compatible"}},
    )

    assert create_response.status_code == 201
    created_project = create_response.json()
    assert created_project["name"] == "第一卷"
    assert created_project["source_lang"] == "ja"
    assert created_project["target_lang"] == "zh-CN"
    assert created_project["provider_config"] == {"kind": "openai_compatible"}

    list_response = await client.get("/api/v1/projects")
    assert list_response.status_code == 200
    assert [project["id"] for project in list_response.json()] == [created_project["id"]]

    read_response = await client.get(f"/api/v1/projects/{created_project['id']}")
    assert read_response.status_code == 200
    assert read_response.json()["id"] == created_project["id"]


async def test_read_project_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/api/v1/projects/{uuid4()}")

    assert response.status_code == 404
