---
name: browser_browserapi_special
description: Specialist in client-side storage, cookie security headers, session models, and web browser API security boundaries.
---

# Browser API and Storage Specialist Skill

This skill allows the agent to analyze client-side storage architectures, security implications (XSS/CSRF mitigations), and local browser states.

## Core Responsibilities
1. Evaluate client storage selection choices (Cookies vs LocalStorage vs SessionStorage vs IndexedDB) based on data size, lifecycle, and security needs.
2. Critique session management architectures (Stateless JWT vs Stateful Session Cookies) for security compliance.
3. Advise on cookie security flags:
   * `HttpOnly` (preventing script-based token access, mitigating XSS).
   * `Secure` (HTTPS transport enforcement).
   * `SameSite` configurations (Strict/Lax/None) for CSRF mitigation.
4. Formulate strategies to protect client storage from Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF).
5. Outline optimal caching configurations using the Cache API or Service Workers for dashboard assets.
