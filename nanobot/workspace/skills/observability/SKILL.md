# Observability Skill

You have access to observability tools that let you query VictoriaLogs and VictoriaTraces to investigate system health, errors, and traces.

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `obs_health` | Check if observability services (VictoriaLogs, VictoriaTraces) are healthy | None |
| `logs_search` | Search logs using LogsQL query | `query` (optional): LogsQL query string, `limit` (optional, default 20): max entries, `start` (optional): start time, `end` (optional): end time |
| `logs_error_count` | Count errors per service over a time window | `start` (optional, default "1h"): time window like "1h", "30m", "24h" |
| `logs_recent_errors` | Get recent error logs from the last hour | None |
| `traces_services` | List all services that have sent traces | None |
| `traces_list` | List recent traces, optionally filter by service | `service` (optional): service name, `limit` (optional, default 10): max traces |
| `traces_get` | Fetch a specific trace by ID | `trace_id` (required): trace ID hex string |

## LogsQL Query Examples

VictoriaLogs uses LogsQL for querying. The backend uses OpenTelemetry standard fields:

- `severity:ERROR` — all error-level logs (OpenTelemetry standard)
- `event:db_query` — logs with specific event name
- `service.name:"Learning Management Service"` — logs from specific service
- `severity:ERROR AND service.name:"backend"` — errors from specific service
- `error` — logs containing "error" in any field

## How to Investigate Errors

When the user asks about errors or system health:

### Step 1: Check observability services health
First, verify the observability stack is working:
```
Call obs_health
```

### Step 2: Search for recent errors
If services are healthy, look for errors:
```
Call logs_error_count with start="1h"
```
This shows error counts per service.

### Step 3: Get detailed error logs
For more details on specific errors:
```
Call logs_search with query="level:error", limit=20, start="1h"
```

### Step 4: Find related traces
If you find a trace ID in the error logs (look for `trace_id` field):
```
Call traces_get with trace_id="<the-trace-id>"
```
This shows the full distributed trace with all spans.

### Step 5: List traces for a service
To see recent traces for a specific service:
```
Call traces_list with service="Learning Management Service", limit=10
```

## Response Guidelines

1. **Summarize, don't dump** — Don't return raw JSON. Summarize findings:
   - "Found 15 errors in the last hour"
   - "Most errors are from the backend service (12 errors)"
   - "The error trace shows a database connection failure"

2. **Include trace IDs when relevant** — If you find interesting errors, mention the trace ID so users can investigate further.

3. **Explain what the error means** — Connect log entries to system behavior:
   - "db_query errors indicate database connectivity issues"
   - "HTTP 500 responses suggest the backend encountered an exception"

4. **Use time ranges appropriately** — Default to "1h" (last hour) unless user specifies otherwise.

## Example Workflows

### "Any errors in the last hour?"
1. Call `logs_error_count` with start="1h"
2. If errors found, call `logs_recent_errors` for details
3. Summarize: "Yes, found X errors. Most are from [service]. The errors show [description]."

### "What went wrong?" or "What went wrong with the last request?"
This is a **multi-step investigation**. Chain the tools in order:

1. **Find recent errors**: Call `logs_search` with `query="severity:ERROR"`, `limit=10`, `start="5m"`
2. **Extract trace ID**: Look at the most recent error log and find the `trace_id` field
3. **Fetch the trace**: Call `traces_get` with that `trace_id`
4. **Analyze the trace**: Look at the span hierarchy to find which span has the error
5. **Summarize concisely**: Combine log evidence + trace evidence into a coherent explanation

Example response format:
> "I found an error in the logs from 2 minutes ago. The log shows a database connection failure (error: 'connection refused'). The trace ID is `abc123...`. Looking at the full trace, the failure occurred in the `db_query` span — the backend tried to connect to PostgreSQL but the database was unavailable. The request completed with HTTP 500."

### "Check system health"
1. **Check observability stack**: Call `obs_health` to verify VictoriaLogs and VictoriaTraces are running
2. **Check for recent errors**: Call `logs_error_count` with start="5m"
3. **If errors found**: Follow the "What went wrong?" workflow above
4. **Report status**: "Observability services are healthy. Found X errors in the last 5 minutes. [Details if any]"

### "Show me traces for the backend"
1. Call `traces_list` with service="Learning Management Service", limit=10
2. Summarize the traces found: "Found 10 traces. Most recent took Xms, involved Y spans"

## Handling "What can you do for observability?"

When asked about observability capabilities:

> I can help you investigate system health and errors:
>
> • **Check service health** — Verify VictoriaLogs and VictoriaTraces are running
> • **Search logs** — Find specific log entries using LogsQL queries
> • **Count errors** — See error counts per service over time windows
> • **Get recent errors** — Show the most recent error logs
> • **List traces** — See recent distributed traces for any service
> • **Fetch trace details** — Get full trace with all spans by trace ID
>
> Ask me things like:
> - "Any errors in the last hour?"
> - "What went wrong?"
> - "Show me traces for the backend"
> - "Is the observability stack healthy?"
