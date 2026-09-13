"""Permissioned read-only MCP tools for the agent's local knowledge boundary."""

from mcp.server.fastmcp import FastMCP

from .config import get_settings
from .retrieval import search_documents, traverse_entities

mcp = FastMCP("nexus-knowledge-tools")


def _allowed(name: str) -> bool:
    return name in {item.strip() for item in get_settings().mcp_allowed_tools.split(",")}


@mcp.tool()
def local_search(query: str) -> list[dict]:
    """Search the local document index. Read-only and allowlisted."""
    if not _allowed("local_search"):
        raise PermissionError("local_search is disabled by MCP_ALLOWED_TOOLS")
    return [
        {"id": doc.id, "title": doc.title, "excerpt": doc.text, "score": score}
        for doc, score in search_documents(query)
    ]


@mcp.tool()
def entity_lookup(query: str) -> list[dict]:
    """Traverse the local entity relationship graph. Read-only and allowlisted."""
    if not _allowed("entity_lookup"):
        raise PermissionError("entity_lookup is disabled by MCP_ALLOWED_TOOLS")
    return [
        {
            "name": entity.name,
            "kind": entity.kind,
            "description": entity.description,
            "related": entity.related,
            "score": score,
        }
        for entity, score in traverse_entities(query)
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
