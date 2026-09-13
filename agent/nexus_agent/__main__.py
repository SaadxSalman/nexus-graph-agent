import uvicorn

from .config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "nexus_agent.api:app", host=settings.agent_host, port=settings.agent_port, reload=False
    )
