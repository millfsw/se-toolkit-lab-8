#!/usr/bin/env python3
"""Entrypoint for nanobot gateway in Docker.

Resolves environment variables into config at runtime, then launches nanobot gateway.
"""

import json
import os
import sys
from pathlib import Path


def resolve_config():
    """Load config.json, inject env var values, write resolved config."""
    config_path = Path(__file__).parent / "config.json"
    resolved_path = Path(__file__).parent / "config.resolved.json"
    
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    
    # Resolve LLM provider API key and base URL from env vars
    llm_api_key = os.environ.get("LLM_API_KEY", "")
    llm_api_base_url = os.environ.get("LLM_API_BASE_URL", "")
    llm_api_model = os.environ.get("LLM_API_MODEL", "")
    
    if llm_api_key:
        config["providers"]["openai"]["apiKey"] = llm_api_key
    if llm_api_base_url:
        config["providers"]["openai"]["apiBase"] = llm_api_base_url
    
    # Resolve model from env var
    if llm_api_model:
        config["agents"]["defaults"]["model"] = llm_api_model
    
    # Resolve gateway host/port
    gateway_host = os.environ.get("NANOBOT_GATEWAY_CONTAINER_ADDRESS", "")
    gateway_port = os.environ.get("NANOBOT_GATEWAY_CONTAINER_PORT", "")
    
    if gateway_host:
        config["gateway"]["host"] = gateway_host
    if gateway_port:
        config["gateway"]["port"] = int(gateway_port)
    
    # Resolve MCP server env vars (backend URL and API key)
    if "mcpServers" in config.get("tools", {}):
        mcp_servers = config["tools"]["mcpServers"]
        
        if "lms" in mcp_servers:
            lms_backend_url = os.environ.get("NANOBOT_LMS_BACKEND_URL", "")
            lms_api_key = os.environ.get("NANOBOT_LMS_API_KEY", "")
            
            if "env" not in mcp_servers["lms"]:
                mcp_servers["lms"]["env"] = {}
            
            if lms_backend_url:
                mcp_servers["lms"]["env"]["NANOBOT_LMS_BACKEND_URL"] = lms_backend_url
            if lms_api_key:
                mcp_servers["lms"]["env"]["NANOBOT_LMS_API_KEY"] = lms_api_key
    
    # Write resolved config
    with open(resolved_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return str(resolved_path)


def main():
    """Resolve config and launch nanobot gateway."""
    resolved_config = resolve_config()
    workspace = os.environ.get("NANOBOT_WORKSPACE", "/app/nanobot/workspace")
    
    # Launch nanobot gateway by importing and running the CLI
    from nanobot.cli.commands import app
    import sys
    
    # Set up sys.argv for the CLI
    sys.argv = [
        "nanobot",
        "gateway",
        "--config", resolved_config,
        "--workspace", workspace,
    ]
    
    app()


if __name__ == "__main__":
    main()
