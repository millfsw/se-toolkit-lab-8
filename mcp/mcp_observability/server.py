"""Stdio MCP server exposing observability operations as typed tools."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable
from typing import Any
from datetime import datetime, timedelta

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

server = Server("observability")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_victorialogs_url: str = ""
_victoriatraces_url: str = ""


def get_victorialogs_url() -> str:
    """Get VictoriaLogs URL from environment or default."""
    return os.environ.get(
        "VICTORIALOGS_URL",
        "http://victorialogs:9428"
    )


def get_victoriatraces_url() -> str:
    """Get VictoriaTraces URL from environment or default."""
    return os.environ.get(
        "VICTORIATRACES_URL",
        "http://victoriatraces:10428"
    )


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------


class _NoArgs(BaseModel):
    """Empty input model for tools that don't need arguments."""


class _LogsSearchArgs(BaseModel):
    query: str = Field(
        default="",
        description="LogsQL query string. Examples: 'level:error', '_stream:{service=\"backend\"}', 'db_query'"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Maximum number of log entries to return (default 20, max 1000)"
    )
    start: str = Field(
        default="",
        description="Start time for query (RFC3339 or relative like '1h', '30m'). Default: 1 hour ago"
    )
    end: str = Field(
        default="",
        description="End time for query (RFC3339 or relative). Default: now"
    )


class _LogsErrorCountArgs(BaseModel):
    start: str = Field(
        default="1h",
        description="Start time for query (relative like '1h', '30m', '24h'). Default: 1 hour ago"
    )


class _TracesListArgs(BaseModel):
    service: str = Field(
        default="",
        description="Service name to filter traces (e.g., 'Learning Management Service')"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of traces to return (default 10, max 100)"
    )


class _TracesGetArgs(BaseModel):
    trace_id: str = Field(
        ...,
        description="Trace ID to fetch (hex string)"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text(data: Any) -> list[TextContent]:
    """Serialize data to a JSON text block."""
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    elif isinstance(data, list):
        payload = [item.model_dump() if isinstance(item, BaseModel) else item for item in data]
    else:
        payload = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]


def _text_summary(text: str) -> list[TextContent]:
    """Return a plain text summary."""
    return [TextContent(type="text", text=text)]


async def _query_victorialogs(query: str, limit: int = 20, start: str = "", end: str = "") -> Any:
    """Query VictoriaLogs using LogsQL.
    
    VictoriaLogs returns a stream of JSON lines (one JSON object per line).
    We parse this into a list of log entries.
    """
    url = get_victorialogs_url()
    
    # Build query parameters
    params = {"query": query, "limit": str(limit)}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{url}/select/logsql/query", params=params)
            response.raise_for_status()
            
            # VictoriaLogs returns newline-delimited JSON (JSON lines)
            # Each line is a separate JSON object
            text = response.text.strip()
            if not text:
                return []  # No results
            
            entries = []
            for line in text.split("\n"):
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        # If a line isn't valid JSON, include it as text
                        entries.append({"raw": line})
            
            return entries
        except httpx.ConnectError as e:
            return {"error": f"Cannot connect to VictoriaLogs at {url}: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"VictoriaLogs error: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"Query error: {type(e).__name__}: {e}"}


async def _query_victoriatraces(path: str, params: dict | None = None) -> Any:
    """Query VictoriaTraces using Jaeger-compatible API."""
    url = get_victoriatraces_url()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            full_url = f"{url}/select/jaeger/api/{path}"
            response = await client.get(full_url, params=params or {})
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError as e:
            return {"error": f"Cannot connect to VictoriaTraces at {url}: {e}"}
        except httpx.HTTPStatusError as e:
            return {"error": f"VictoriaTraces error: {e.response.status_code} - {e.response.text}"}
        except Exception as e:
            return {"error": f"Query error: {type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def _logs_search(args: _LogsSearchArgs) -> list[TextContent]:
    """Search logs using LogsQL."""
    result = await _query_victorialogs(
        query=args.query or "_stream:*",
        limit=args.limit,
        start=args.start,
        end=args.end
    )
    return _text(result)


async def _logs_error_count(args: _LogsErrorCountArgs) -> list[TextContent]:
    """Count errors per service over a time window."""
    # Query for error-level logs using 'severity' field (OpenTelemetry standard)
    query = "severity:ERROR"
    result = await _query_victorialogs(query=query, limit=500, start=args.start)
    
    # Format a summary
    if isinstance(result, dict) and "error" in result:
        return _text_summary(f"Error counting failed: {result['error']}")
    
    # Count errors by service from the results
    service_counts: dict[str, int] = {}
    if isinstance(result, list):
        for entry in result:
            service = entry.get("service.name", entry.get("service", "unknown"))
            service_counts[service] = service_counts.get(service, 0) + 1
    
    # Sort by count descending
    sorted_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)
    
    summary_lines = ["Error count by service (last {}):".format(args.start or "1h")]
    if sorted_services:
        for service, count in sorted_services[:10]:
            summary_lines.append(f"  - {service}: {count} errors")
    else:
        summary_lines.append("  No errors found in the time window")
    
    return _text_summary("\n".join(summary_lines))


async def _logs_recent_errors(args: _NoArgs) -> list[TextContent]:
    """Get recent error logs across all services."""
    query = "severity:ERROR"
    result = await _query_victorialogs(query=query, limit=20, start="1h")
    return _text(result)


async def _traces_list(args: _TracesListArgs) -> list[TextContent]:
    """List recent traces for a service."""
    params = {"limit": str(args.limit)}
    if args.service:
        params["service"] = args.service
    
    result = await _query_victoriatraces("traces", params=params)
    return _text(result)


async def _traces_get(args: _TracesGetArgs) -> list[TextContent]:
    """Fetch a specific trace by ID."""
    result = await _query_victoriatraces(f"traces/{args.trace_id}")
    return _text(result)


async def _traces_services(args: _NoArgs) -> list[TextContent]:
    """List all services with traces."""
    result = await _query_victoriatraces("services")
    return _text(result)


async def _health_check(args: _NoArgs) -> list[TextContent]:
    """Check if observability services are healthy."""
    status = {}
    
    # Check VictoriaLogs
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{get_victorialogs_url()}/")
            status["victorialogs"] = "healthy" if resp.status_code == 200 else f"unhealthy ({resp.status_code})"
    except Exception as e:
        status["victorialogs"] = f"unhealthy: {e}"
    
    # Check VictoriaTraces
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{get_victoriatraces_url()}/")
            status["victoriatraces"] = "healthy" if resp.status_code == 200 else f"unhealthy ({resp.status_code})"
    except Exception as e:
        status["victoriatraces"] = f"unhealthy: {e}"
    
    return _text(status)


# ---------------------------------------------------------------------------
# Registry: tool name -> (input model, handler, Tool definition)
# ---------------------------------------------------------------------------

_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]

_TOOLS: dict[str, _Registry] = {}


def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (
        model,
        handler,
        Tool(name=name, description=description, inputSchema=schema),
    )


_register(
    "obs_health",
    "Check if observability services (VictoriaLogs, VictoriaTraces) are healthy.",
    _NoArgs,
    _health_check,
)

_register(
    "logs_search",
    "Search logs using LogsQL query. Use for finding specific log entries by keyword, service, level, etc.",
    _LogsSearchArgs,
    _logs_search,
)

_register(
    "logs_error_count",
    "Count errors per service over a time window. Returns summary of error counts grouped by service.",
    _LogsErrorCountArgs,
    _logs_error_count,
)

_register(
    "logs_recent_errors",
    "Get recent error logs from the last hour across all services. Returns up to 20 most recent errors.",
    _NoArgs,
    _logs_recent_errors,
)

_register(
    "traces_services",
    "List all services that have sent traces to VictoriaTraces.",
    _NoArgs,
    _traces_services,
)

_register(
    "traces_list",
    "List recent traces. Optionally filter by service name.",
    _TracesListArgs,
    _traces_list,
)

_register(
    "traces_get",
    "Fetch a specific trace by its trace ID. Returns full trace with all spans.",
    _TracesGetArgs,
    _traces_get,
)


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
