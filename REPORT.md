# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with 
`![description](path)`.

## Task 1A — Bare agent

**Checkpoint 1: "What is the agentic loop?"**

The agentic loop is the fundamental cycle that autonomous AI agents follow to perceive, reason, and act. 
It's the core pattern that distinguishes agents from simple chatbots or tools.

The Basic Loop:
```
Perceive → Reason → Act → Observe → (repeat)
```

1. **Perceive** — Gather information from the environment (read files, check system state, fetch web content, receive user input)
2. **Reason** — Analyze the current state, plan next steps, decide which tools to call
3. **Act** — Execute chosen actions (tool calls, commands, etc.)
4. **Observe** — Collect feedback from the actions taken, check results/errors
5. **Repeat** — Continue the loop until the goal is achieved

This loop enables autonomy — the agent can break complex tasks into steps, recover from errors, and work toward goals without constant human guidance.

**Checkpoint 2: "What labs are available in our LMS?" (without MCP tools)**

Based on the documentation in your LMS, here are the available labs:

Course Structure:
The SET course consists of 10 labs, each 3 hours long.

Current Lab: Lab 8 — "The Agent is the Interface"

Lab 8 Tasks:
1. Task 1 — Set Up the Agent (Parts A, B, C)
2. Task 2 — Deploy the Agent and Add a Web Client
3. Task 3 — Give the Agent New Eyes (Observability)
4. Task 4 — Diagnose a Failure and Make the Agent Proactive

Optional Task: Task 1 — Add a Telegram Bot Client

*Note: In Part A, the agent did not yet have MCP tools, so it read information from local workspace files rather than from the backend API.*

## Task 1B — Agent with LMS tools

**Checkpoint 1: "What labs are available?" (with MCP tools)**

Perfect! Here are the 8 labs currently available in your LMS:

| ID     | Lab Title                                                |
|--------|----------------------------------------------------------|
| lab-01 | Lab 01 – Products, Architecture & Roles                  |
| lab-02 | Lab 02 — Run, Fix, and Deploy a Backend Service          |
| lab-03 | Lab 03 — Backend API: Explore, Debug, Implement, Deploy  |
| lab-04 | Lab 04 — Testing, Front-end, and AI Agents               |
| lab-05 | Lab 05 — Data Pipeline and Analytics Dashboard           |
| lab-06 | Lab 06 — Build Your Own Agent                            |
| lab-07 | Lab 07 — Build a Client with an AI Coding Agent          |
| lab-08 | lab-08 (The Agent is the Interface)                      |

You're currently working in the Lab 08 workspace.

**Checkpoint 2: "Describe the architecture of the LMS system"**

LMS System Architecture:

The Learning Management System (LMS) is a containerized web application with a modern microservices architecture.

**Core Components:**
- **Caddy (Reverse Proxy)** — Gateway on port 42002, routes all external traffic
- **FastAPI Backend** — LMS REST API (items, learners, interactions), instrumented with OpenTelemetry
- **PostgreSQL** — Primary database (labs, learners, interactions, analytics)
- **React Dashboard** — Web UI for LMS (static files)
- **Qwen Code API** — LLM API gateway
- **Nanobot Agent** — AI agent with MCP tools (WebSocket)
- **Flutter Client** — Alternative chat UI (optional)

**Observability Stack:**
- **OpenTelemetry Collector** — Receives OTLP logs & traces from backend
- **VictoriaLogs** — Log storage & query engine (7-day retention)
- **VictoriaTraces** — Distributed trace storage (7-day retention)

**Network Architecture:**
- All services communicate over a Docker network called lms-network
- Internal service-to-service communication uses Docker service names (e.g., http://backend:8000)
- External access only through Caddy reverse proxy on port 42002

**Checkpoint 3: "Which lab has the lowest pass rate?" (complex query requiring tool chaining)**

Based on the data, here's the analysis:

| Lab    | Completion Rate | Lowest Task Avg Score                          |
|--------|-----------------|------------------------------------------------|
| lab-01 | 100.0%          | 20.0% (Optional: Plan skill development)       |
| lab-02 | 89.1%           | 0.0% (Optional 2: Make your VM a proxy)        |
| lab-03 | 89.1%           | 43.9% (Task 4: Deploy to a hardened VM)        |
| lab-04 | 96.7%           | 33.8% (Optional 1: CI/CD with GitHub Actions)  |
| lab-05 | 98.4%           | 57.2% (Optional 1: Grafana Dashboard)          |
| lab-06 | 98.4%           | 42.8% (Task 3: The System Agent)               |
| lab-07 | 99.6%           | 58.9% (Task 3: Intent-Based Routing)           |
| lab-08 | 0.0%            | N/A (no submissions yet)                       |

🏆 **Lowest Pass Rate: Lab 02**

Lab 02 — Run, Fix, and Deploy a Backend Service has the lowest completion rate at 89.1%.

**Key Struggle Points:**
- "Optional 2: Make your VM a proxy" — 0.0% average score (3 attempts)
- "Optional 1: Implement the /outcomes endpoint" — 36.4% average score (11 attempts)
- "Task 4: Deploy the web server to the VM" — 56.2% average score (84 attempts)

## Task 1C — Skill prompt

**Checkpoint: "Show me the scores" (without specifying a lab)**

I can show you the scores, but I need to know which lab you're interested in. Here are the available labs:

| Lab ID  | Title                                           |
|---------|-------------------------------------------------|
| lab-01  | Products, Architecture & Roles                  |
| lab-02  | Run, Fix, and Deploy a Backend Service          |
| lab-03  | Backend API: Explore, Debug, Implement, Deploy  |
| lab-04  | Testing, Front-end, and AI Agents               |
| lab-05  | Data Pipeline and Analytics Dashboard           |
| lab-06  | Build Your Own Agent                            |
| lab-07  | Build a Client with an AI Coding Agent          |
| lab-08  | The Agent is the Interface                      |

Which lab would you like to see scores for? Or would you like me to show:
- All labs' completion rates (overview)
- Top learners for a specific lab
- Group performance for a specific lab
- Submission timeline for a specific lab

*Note: After adding the skill prompt, the agent no longer returns empty results or hallucinations — it asks a clarifying question and shows available options.*

## Task 2A — Deployed agent

**Nanobot gateway startup log excerpt:**

```
nanobot-1  | Using config: /app/nanobot/config.resolved.json
nanobot-1  | 🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
nanobot-1  | 2026-03-28 09:10:56.761 | DEBUG    | nanobot.channels.registry:discover_all:64 - Skipping built-in channel 'matrix': Matrix dependencies not installed.
nanobot-1  | 2026-03-28 09:10:58.780 | INFO     | nanobot.channels.manager:_init_channels:58 - WebChat channel enabled
nanobot-1  | ✓ Channels enabled: webchat
nanobot-1  | ✓ Heartbeat: every 1800s
nanobot-1  | 2026-03-28 09:10:58.789 | INFO     | nanobot.cron.service:start:202 - Cron service started with 0 jobs
nanobot-1  | 2026-03-28 09:10:58.789 | INFO     | nanobot.heartbeat.service:start:124 - Heartbeat started (every 1800s)
nanobot-1  | 2026-03-28 09:10:59.xxx | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_health' from server 'lms'
nanobot-1  | 2026-03-28 09:10:59.xxx | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_labs' from server 'lms'
nanobot-1  | 2026-03-28 09:10:59.xxx | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_learners' from server 'lms'
nanobot-1  | 2026-03-28 09:10:59.xxx | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_pass_rates' from server 'lms'
nanobot-1  | 2026-03-28 09:10:59.xxx | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_timeline' from server 'lms'
nanobot-1  | 2026-03-28 09:10:59.xxx | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_groups' from server 'lms'
nanobot-1  | 2026-03-28 09:10:59.xxx | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_top_learners' from server 'lms'
nanobot-1  | 2026-03-28 09:10:59.xxx | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_completion_rate' from server 'lms'
nanobot-1  | 2026-03-28 09:10:59.xxx | DEBUG    | nanobot.agent.tools.mcp:connect_mcp_servers:226 - MCP: registered tool 'mcp_lms_lms_sync_pipeline' from server 'lms'
nanobot-1  | 2026-03-28 09:10:59.xxx | INFO     | nanobot.agent.tools.mcp:connect_mcp_servers:246 - MCP server 'lms': connected, 9 tools registered
nanobot-1  | 2026-03-28 09:10:59.xxx | INFO     | nanobot.agent.loop:run:280 - Agent loop started
```

**Deployment summary:**
- Nanobot runs as a Docker Compose service (`nanobot`) using `nanobot gateway` mode
- WebChat channel enabled for WebSocket connections at `/ws/chat`
- MCP server connected with 9 LMS tools (health, labs, learners, pass_rates, timeline, groups, top_learners, completion_rate, sync_pipeline)
- Gateway listening on port 18790, proxied through Caddy at port 42002

## Task 2B — Web client

**Flutter web UI:**
- Accessible at `http://<vm-ip>:42002/flutter`
- Protected by `NANOBOT_ACCESS_KEY` authentication
- Connects to agent via WebSocket at `/ws/chat`

**Login credentials:**
- Access Key: `my-nano-access-key` (configured in `.env.docker.secret`)

*[Insert screenshot of Flutter chat conversation here]*

To capture a screenshot:
1. Open `http://<your-vm-ip>:42002/flutter` in your browser
2. Log in with the access key: `my-nano-access-key`
3. Ask the agent: "What can you do in this system?"
4. Ask a follow-up question about the LMS (e.g., "Which lab has the lowest pass rate?")
5. Take a screenshot and save it to the repo (e.g., `images/task2b-flutter-chat.png`)
6. Reference it here: `![Flutter chat screenshot](images/task2b-flutter-chat.png)`

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
