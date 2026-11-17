
"""StateInfo MCP Server - exposes all six StateInfoWebAPI endpoints."""

import logging
import os
import re

import httpx
from fastmcp import FastMCP

# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("StateInfoMCPServer")

# --------------------------------------------------
# Configuration
# --------------------------------------------------

API_BASE_URL = os.getenv(
    "STATEINFO_API_BASE_URL",
    "http://4.249.235.43:80"
).rstrip("/")

API_TIMEOUT = float(
    os.getenv("STATEINFO_API_TIMEOUT_SECONDS", "30")
)

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("PORT", "8001"))

# --------------------------------------------------
# MCP Server
# --------------------------------------------------

mcp = FastMCP(
    "StateInfoMCPServer",
    instructions=(
        "Use these tools to retrieve authoritative US state "
        "information from StateInfoWebAPI. "
        "Never invent state facts."
    )
)

# --------------------------------------------------
# HTTP helper
# --------------------------------------------------

async def api_get(
    path: str,
    params: dict | None = None
):
    """Call a known StateInfoWebAPI endpoint."""

    # Restrict backend calls to approved routes.
    allowed_paths = {
        "/health",
        "/info",
        "/api/states/GetAll",
        "/api/states/GetAllByPopulation",
        "/api/states/GetByCode",
        "/api/states/GetByName",
    }

    if path not in allowed_paths:
        raise ValueError("API endpoint is not allowed")

    try:
        async with httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=API_TIMEOUT,
            follow_redirects=False
        ) as client:

            logger.info(
                "Calling StateInfoWebAPI: %s%s",
                API_BASE_URL,
                path
            )

            response = await client.get(
                path,
                params=params
            )

            logger.info(
                "API Response: HTTP %s | URL: %s",
                response.status_code,
                response.request.url
            )

            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as exc:

        logger.error(
            "StateInfoWebAPI returned HTTP %s for %s",
            exc.response.status_code,
            exc.request.url
        )

        raise RuntimeError(
            f"StateInfoWebAPI returned HTTP "
            f"{exc.response.status_code}"
        ) from exc

    except httpx.RequestError as exc:

        logger.error(
            "Unable to reach StateInfoWebAPI: %s",
            exc
        )

        raise RuntimeError(
            "StateInfoWebAPI is unavailable or timed out"
        ) from exc

    except ValueError as exc:

        logger.error(
            "Invalid JSON response from StateInfoWebAPI: %s",
            exc
        )

        raise RuntimeError(
            "StateInfoWebAPI returned invalid JSON"
        ) from exc


# --------------------------------------------------
# MCP Tool 1 - Health
# --------------------------------------------------

@mcp.tool()
async def get_health() -> dict:
    """Check StateInfoWebAPI health status."""

    return await api_get("/health")


# --------------------------------------------------
# MCP Tool 2 - Get All States
# --------------------------------------------------

@mcp.tool()
async def get_all_states() -> list[dict]:
    """Retrieve all US state records."""

    return await api_get("/api/states/GetAll")


# --------------------------------------------------
# MCP Tool 3 - Population
# --------------------------------------------------

@mcp.tool()
async def get_states_by_population(
    populationCount: int
) -> list[dict]:
    """Retrieve states with population >= populationCount."""

    if (
        isinstance(populationCount, bool)
        or not isinstance(populationCount, int)
        or populationCount < 0
    ):
        raise ValueError(
            "populationCount must be a nonnegative integer"
        )

    return await api_get(
        "/api/states/GetAllByPopulation",
        {"populationCount": populationCount}
    )


# --------------------------------------------------
# MCP Tool 4 - State Code
# --------------------------------------------------

@mcp.tool()
async def get_state_by_code(
    stateCode: str
) -> list[dict]:
    """Retrieve a state by its two-letter code."""

    code = stateCode.strip().upper()

    if not re.fullmatch(r"[A-Z]{2}", code):
        raise ValueError(
            "stateCode must contain exactly two letters"
        )

    return await api_get(
        "/api/states/GetByCode",
        {"stateCode": code}
    )


# --------------------------------------------------
# MCP Tool 5 - State Name
# --------------------------------------------------

@mcp.tool()
async def get_state_by_name(
    stateName: str
) -> list[dict]:
    """Retrieve a state by its name."""

    name = stateName.strip()

    if not name:
        raise ValueError(
            "stateName cannot be blank"
        )

    return await api_get(
        "/api/states/GetByName",
        {"stateName": name}
    )


# --------------------------------------------------
# MCP Tool 6 - API Information
# --------------------------------------------------

@mcp.tool()
async def get_api_info() -> dict:
    """Retrieve StateInfoWebAPI description and version."""

    return await api_get("/info")


# --------------------------------------------------
# Application startup
# --------------------------------------------------

if __name__ == "__main__":

    logger.info("Starting StateInfoMCPServer")
    logger.info("Backend API: %s", API_BASE_URL)
    logger.info(
        "MCP Endpoint: http://%s:%s/mcp",
        MCP_HOST,
        MCP_PORT
    )

   mcp.run(
        transport="http",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8001")),
        path="/mcp"
    )
