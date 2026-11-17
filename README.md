# StateInfoMCPServer

A Python FastMCP server exposing **all six** routes defined in the uploaded StateInfoWebAPI `main.py`. Calls are forwarded over HTTP; this server does not connect to SQL Server.

| MCP tool | StateInfoWebAPI route | Arguments |
|---|---|---|
| `get_health` | `GET /health` | — |
| `get_all_states` | `GET /api/states/GetAll` | — |
| `get_states_by_population` | `GET /api/states/GetAllByPopulation` | `populationCount` (int >= 0) |
| `get_state_by_code` | `GET /api/states/GetByCode` | `stateCode` (two letters) |
| `get_state_by_name` | `GET /api/states/GetByName` | `stateName` (nonblank) |
| `get_api_info` | `GET /info` | — |

## Local setup (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:STATEINFO_API_BASE_URL='http://localhost:8000'
$env:PORT='8001'
python -m app.main
```

Connect an MCP Inspector to `http://localhost:8001/mcp` using **Streamable HTTP**. StateInfoWebAPI must be running separately. Run tests with `pytest -q`.

## Container and AKS

Build image: `docker build -t stateinfo-mcp:latest .`

Push the image to ACR using your existing GitHub Actions or ACR workflow. Edit `k8s/deployment.yaml` to replace `REPLACE_ACR_NAME` and `REPLACE_STATEINFO_API_SERVICE` with your actual registry and Kubernetes service name/port, then deploy it. The service is **ClusterIP only**, not public. Ensure AKS can pull from ACR via its managed identity/appropriate AcrPull role. For access from outside AKS, configure authenticated HTTPS ingress and authorization before exposing `/mcp`.

## Security and deployment notes

- Tool arguments never contain database credentials or arbitrary URLs.
- Keep the MCP service private until authentication, network restrictions and rate limits are in place.
- The upstream API must independently enforce its own authorization; this adapter does not add upstream authentication.
- `STATEINFO_API_BASE_URL` should be an internal service URL in AKS, not `localhost`.
- `get_state_by_name` uses exact matching because the API SQL query uses `=`.
- StateInfoWebAPI currently uses SQL username/password and `TrustServerCertificate=yes`; harden its database connection separately before production.
- This is a static mapping of the six endpoints in the supplied API source. New endpoints require adding a tool or implementing a reviewed OpenAPI sync.
