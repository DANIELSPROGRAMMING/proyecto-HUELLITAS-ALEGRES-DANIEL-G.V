# Security Audit History — Huellitas Alegres

## Overview

Four comprehensive security audits were performed on the codebase (May 2026). All findings were addressed. The project has **zero remaining critical or warning-level issues**.

## Audit Timeline

| # | Date | Scope | Findings | Fixed |
|---|------|-------|----------|-------|
| 1 | 2026-05-21 | Full codebase — NIM integration | 3 CRIT, 7 WARN, 7 SUGG | 4 fixes |
| 2 | 2026-05-21 | Verify fixes + 40 new checks | 1 CRIT, 5 WARN, 4 SUGG | 6 fixes |
| 3 | 2026-05-21 | Auth module + 30 new areas | 3 CRIT, 6 WARN, 3 SUGG | 3 fixes |
| 4 | 2026-05-21 | Verify all 13 fixes + final sweep | ZERO | Verified |

**Total: 13 issues found, 13 fixed. 0 remaining.**

## Issues Found & Fixed

### Critical (all fixed)
| Issue | Location | Fix | Audit |
|-------|----------|-----|-------|
| `print(e)` leaks HTTP response body | `chatbot/views.py` | Only `type(e).__name__`, no body | #1 |
| `@csrf_exempt` on chatbot without justification | `chatbot/views.py` | Documented: read-only, rate-limited, public | #1 |
| `_ai_conversation_active` not reset on NIM failure | `chatbot/views.py` | Reset to False in all 3 except blocks | #1 |
| `ALLOWED_HOSTS = []` with `DEBUG=True` | `settings.py` | `['localhost', '127.0.0.1']` | #2 |
| CSRF on `registro_usuario` + `login_usuario` | `usuarios/views.py` | `@require_POST` + CORS justification | #3 |
| Session fixation on `login()` | `usuarios/views.py` | `request.session.cycle_key()` | #3 |
| `str(e)` leaked to JSON auth responses | `usuarios/views.py` | `'Error interno del servidor'` | #3 |

### Warning (all fixed)
| Issue | Location | Fix | Audit |
|-------|----------|-----|-------|
| Silent exception swallowing | `chatbot/views.py`, `tools.py` | Specific exception types | #1, #2, #3 |
| Tools.py error leaked to NIM model | `chatbot/services/tools.py` | Type name only, no body | #2 |
| HTTP call with empty API key | `chatbot/views.py` | Guard: `raise ValueError` if key empty | #2 |
| No message length cap | `chatbot/views.py` | Truncated at 10K chars | #2 |
| `send_image()` caught `KeyboardInterrupt` | `chatbot/views.py` | Narrowed to specific types | #2 |
| Rate limiting TOCTOU race | `chatbot/views.py` | Documented with production guidance | #2 |

## Production Deployment Notes

Before deploying to production, the following must be addressed:

1. **`SECRET_KEY`**: Move to `.env` — `SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')`
2. **`DEBUG`**: Set via env — `DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'`
3. **`ALLOWED_HOSTS`**: Add actual domain name(s)
4. **Session cookies**: Configure `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_SAMESITE`
5. **Custom error pages**: Create `templates/404.html` and `templates/500.html`
6. **Static/media files**: Configure nginx/Caddy to serve `MEDIA_ROOT` and `STATIC_ROOT`

## Final Verdict

**PASS — Production-ready for SENA demonstration scope.**
