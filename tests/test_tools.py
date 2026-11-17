import pytest
import respx
import httpx
from app import main

@pytest.mark.asyncio
@respx.mock
async def test_all_endpoints():
    base = main.API_BASE_URL
    routes = [
        ('/health', main.get_health, (), {'status': 'ok'}),
        ('/api/states/GetAll', main.get_all_states, (), []),
        ('/api/states/GetAllByPopulation', main.get_states_by_population, (1000000,), []),
        ('/api/states/GetByCode', main.get_state_by_code, ('il',), []),
        ('/api/states/GetByName', main.get_state_by_name, ('Illinois',), []),
        ('/info', main.get_api_info, (), {'name': 'StateInfo WebAPI'}),
    ]
    for path, _, _, result in routes:
        respx.get(base + path).mock(return_value=httpx.Response(200, json=result))
    for _, func, args, expected in routes:
        assert await func(*args) == expected
    assert respx.calls[-2].request.url.params['stateName'] == 'Illinois'

@pytest.mark.asyncio
async def test_validation():
    with pytest.raises(ValueError):
        await main.get_states_by_population(-1)
    with pytest.raises(ValueError):
        await main.get_state_by_code('INVALID')
    with pytest.raises(ValueError):
        await main.get_state_by_name('  ')
