import pytest
import respx
import httpx

from fastmcp import Client
from app import main


@pytest.mark.asyncio
@respx.mock
async def test_all_endpoints():
    base = main.API_BASE_URL

    routes = [
        ("/health", "get_health", {}, {"status": "ok"}),
        ("/api/states/GetAll", "get_all_states", {}, []),
        (
            "/api/states/GetAllByPopulation",
            "get_states_by_population",
            {"populationCount": 1000000},
            [],
        ),
        (
            "/api/states/GetByCode",
            "get_state_by_code",
            {"stateCode": "il"},
            [],
        ),
        (
            "/api/states/GetByName",
            "get_state_by_name",
            {"stateName": "Illinois"},
            [],
        ),
        (
            "/info",
            "get_api_info",
            {},
            {"name": "StateInfo WebAPI"},
        ),
    ]

    for path, _, _, result in routes:
        respx.get(base + path).mock(
            return_value=httpx.Response(200, json=result)
        )

    async with Client(main.mcp) as client:
        for _, tool_name, arguments, expected in routes:
            result = await client.call_tool(
                tool_name,
                arguments,
                raise_on_error=True,
            )

            assert result.data == expected


@pytest.mark.asyncio
async def test_validation():
    async with Client(main.mcp) as client:
        result = await client.call_tool(
            "get_states_by_population",
            {"populationCount": -1},
            raise_on_error=False,
        )

        assert result.is_error