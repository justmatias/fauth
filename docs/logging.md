# Structured Logging

FAuth uses [`structlog`](https://www.structlog.org/) for structured logging across all security-sensitive operations. **FAuth does not call `structlog.configure()`** — your application owns the processor pipeline. If you never configure structlog, the default `dev` renderer is used (coloured, human-readable text).

## Configuring log output

Configure structlog once in your application startup — FAuth (and any other structlog-based library) will follow:

```python
import structlog

# Development — human-readable coloured text
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.dev.ConsoleRenderer(),
    ],
)

# Production — JSON lines for log aggregators (Datadog, ELK, etc.)
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
)
```

## What gets logged

| Event                   | Level     | Context                                                                        |
| ----------------------- | --------- | ------------------------------------------------------------------------------ |
| `login_token_issued`    | `info`    | `sub`                                                                          |
| `token_decoded`         | `debug`   | `sub`, `token_type`                                                            |
| `user_authenticated`    | `debug`   | `sub`                                                                          |
| `authentication_failed` | `warning` | `reason` (`missing_token`, `token_expired`, `invalid_token`, `user_not_found`) |
| `authorization_failed`  | `warning` | `reason` (`inactive_user`, `missing_role`, `missing_permission`)               |

## Example log output

With `ConsoleRenderer()` (default):

```
2026-04-01 10:30:15 [info     ] login_token_issued             sub=user-123
2026-04-01 10:30:16 [debug    ] token_decoded                  sub=user-123 token_type=access
2026-04-01 10:31:00 [warning  ] authentication_failed          reason=token_expired
```

With `JSONRenderer()`:

```json
{"sub": "user-123", "event": "login_token_issued", "level": "info", "timestamp": "2026-04-01T13:30:15Z"}
{"reason": "token_expired", "event": "authentication_failed", "level": "warning", "timestamp": "2026-04-01T13:31:00Z"}
```
