# Authentication and authorization — bearer tokens, JWT signatures, and the OAuth 2.1 consolidation

*What a JWT signature actually proves, why anyone can read a token's payload without the secret key, and the specification revision that removed the exact grant type a 2022-era book teaches as the standard pattern.*

**Level:** L4 · **Prerequisites:** [15 ASGI request handling and dependency injection](15_asgi_request_handling_and_dependency_injection.md)
**Covers:** PY-17
**Sources:** Tragura, *Building Python Microservices with FastAPI*, ch.7 (2022) — the OAuth2 password-grant and JWT material, cited as the migration source for a still-current mechanism built on a now-deprecated grant · OAuth 2.1 specification, oauth.net

---

## 1. The problem this solves

A traditional server-rendered application authenticates a user once, at login, and relies on a session cookie the server itself can look up on every later request. A REST API serving a mobile app, a single-page frontend, and possibly other backend services all at once cannot rely on the same shared-session assumption — there may be no server-side session store at all, and the client may not be a browser willing to carry a cookie automatically. OAuth2 answers this with a token the client holds and presents on every request: something the server can verify **without a database lookup**, carrying enough information on its own to answer "who is this, and what are they allowed to do" — which is exactly the property a signed token, rather than an opaque session ID, provides.

A second, related problem sits alongside the first: an API that needs to know a user's *identity* — not merely that some previously-issued token is still valid, but who this specific person actually is, verified by a party the API trusts to make that determination — without maintaining its own username-and-password database at all. Delegating that verification to an external identity provider (a company's own single sign-on system, a consumer identity platform) means the API never handles a raw password in the first place, and never becomes the thing an attacker targets to harvest credentials, because it never stores any.

The token itself needs its own answer to a narrower, sharper question: how does a server trust a string the *client* is handing back to it? A plain username and password sent on every request — chapter 15's own material already establishes HTTP Basic authentication does exactly this — works, but sends the actual credential on every single call, multiplying the exposure if any one request is intercepted. A **JSON Web Token** exists to break that link: a server issues a token once, signs it cryptographically, and every later request presents the token instead of the underlying credential — verifiable by checking the signature, not by looking anything up, which is the direct payoff FastAPI's `Depends()`-based security scheme (chapter 15's own mechanism, applied here) builds on.

---

## 2. The mechanism, built up

### 2.1 HTTP Basic sends the real credential, base64-encoded, on every single request

```text
Authorization: Basic YWxleGFuZHJvOnNlY3JldA==
```

`YWxleGFuZHJvOnNlY3JldA==` is not encrypted — it is `alexandro:secret`, base64-encoded, trivially reversible by anyone who intercepts it. Basic authentication's entire security model rests on the transport itself being encrypted (TLS), because the scheme provides none on its own: the actual password crosses the wire, in a recoverable form, on every request, which is precisely why it has fallen out of favor for anything beyond the simplest internal tooling — the exposure from a single intercepted request is the full credential, not a narrower, revocable token.

### 2.2 `OAuth2PasswordBearer` is a `Depends()`-compatible scheme, not a separate authentication system

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    ...
```

`OAuth2PasswordBearer` is, underneath, an ordinary callable — chapter 15's entire dependency mechanism applies to it unchanged. Calling it extracts the bearer token from the request's `Authorization` header (or raises `401` if the header is missing or malformed) and hands the raw token string to whatever depends on it; `tokenUrl` exists purely to tell interactive API documentation where a client should go to actually obtain a token, and has no bearing on request handling at all. Nothing about this scheme validates the token's contents — that is a separate step, section 2.4 covers directly, and `OAuth2PasswordBearer`'s own job stops at "here is the string the client sent."

### 2.3 A JWT's three parts are base64, not encryption — the payload is readable by anyone, with or without the secret key

```python
import jwt
token = jwt.encode({"sub": "alexandro"}, "some-secret", algorithm="HS256")
print(jwt.get_unverified_header(token))
print(jwt.decode(token, options={"verify_signature": False}))
```

```text
{'alg': 'HS256', 'typ': 'JWT'}
{'sub': 'alexandro'}
```

```mermaid
graph LR
    HEADER["header<br/>{alg, typ}"] -->|"base64url,<br/>readable by anyone"| DOT1["."]
    DOT1 --> PAYLOAD["payload<br/>{sub, exp, scopes, ...}"]
    PAYLOAD -->|"base64url,<br/>readable by anyone"| DOT2["."]
    DOT2 --> SIG["signature<br/>HMAC(header + '.' + payload, secret_key)"]
```

Both calls succeed with **no key at all**. A JWT is three base64url-encoded segments — a header, a payload, and a signature — joined by dots, and base64 is an encoding, not an encryption scheme: reversing it requires no secret, which is exactly what `get_unverified_header` and the `verify_signature=False` decode both demonstrate directly. The signature is what makes a JWT trustworthy, not the payload's confidentiality — a JWT proves the issuer produced this exact content and it has not been altered since, and it proves nothing at all about who is allowed to *read* that content, which is precisely why Tragura's own material, cited by this node, warns explicitly against placing sensitive information directly in a token's payload.

### 2.4 The signature is what turns a readable string into a trustworthy one

```python
tampered_token = token[:-1] + ("A" if token[-1] != "A" else "B")
jwt.decode(tampered_token, "some-secret", algorithms=["HS256"])
```

```text
jwt.exceptions.InvalidSignatureError: Signature verification failed
```

Flipping a single character anywhere in the token — including inside the payload segment itself — invalidates the signature, because the signature is computed over the header and payload together using the secret key, and any change to either segment produces a signature that no longer matches what a correct recomputation would produce. This is the actual security guarantee a JWT provides: not that the payload is hidden, but that it cannot be modified without possession of the secret key used to sign it, which is precisely why that key has to be kept genuinely secret — anyone holding it can mint a token claiming to be any user at all, indistinguishable from a token the real server issued.

### 2.5 Expiration is a claim inside the payload, enforced by the verifying code, not by the token itself

```python
import jwt
from datetime import datetime, timedelta, timezone

expired = jwt.encode(
    {"sub": "alexandro", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
    "some-secret", algorithm="HS256",
)
jwt.decode(expired, "some-secret", algorithms=["HS256"])
```

```text
jwt.exceptions.ExpiredSignatureError: Signature has expired
```

`exp` is an ordinary field in the payload, and a token past its `exp` still has a perfectly valid signature — the library's `decode` call checks the current time against that field as a separate step from signature verification, raising a distinct exception when it fails. This is why a short-lived access token, refreshed regularly, limits exposure from a leaked token far better than a long-lived one: the token remains cryptographically valid and completely readable for its entire lifetime, and `exp` is the only thing that eventually makes a verifier stop accepting it.

A **refresh token** is the standard answer to the tension this creates between "short-lived enough to limit exposure" and "long-lived enough that a user is not forced to log in again every few minutes." It is issued alongside the access token, typically with a much longer lifetime and a narrower purpose — it is presented only to a dedicated token-refresh endpoint, never to an ordinary API route, and its only job is minting a fresh, short-lived access token without requiring the user's credential again. This splits the exposure risk in two: a leaked access token is dangerous for minutes, not days, while a leaked refresh token is dangerous for longer but is presented far less often, to a narrower endpoint, which is precisely the kind of asymmetric risk profile OAuth 2.1's own additional requirement — that a public client's refresh token be sender-constrained or single-use — is designed to tighten further.

### 2.6 A verifier must restrict which algorithms it will accept — the algorithm is also just a claim, in the header this time

```python
jwt.decode(token, "some-secret", algorithms=["HS512"])
```

```text
jwt.exceptions.InvalidAlgorithmError: The specified alg value is not allowed
```

`algorithms=[...]` is not optional ceremony — it is the verifying code explicitly refusing to trust the `alg` field the token itself claims in its header, requiring the caller to state up front which algorithms are acceptable rather than letting the token dictate how it should be checked. This exists because of a well-documented class of attack against JWT libraries that once trusted the header's own `alg` claim blindly: a token presenting `alg: none`, or an algorithm mismatched against the key type in a way that lets an attacker forge a valid-looking signature, can defeat verification entirely in a library that reads the algorithm from the token rather than requiring it from the caller. Every current JWT library requires this list explicitly for exactly this reason, and omitting it — passing no `algorithms` argument at all, where a library's API even allows that — reopens exactly the hole the explicit list exists to close.

### 2.7 Scope-based authorization layers "what is this token allowed to do" on top of "whose token is this"

```python
from fastapi import Security
from fastapi.security import SecurityScopes

def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    token_scopes = payload.get("scopes", [])
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(status_code=403, detail=f"Not enough permissions, need {scope}")
    return payload["sub"]

@app.get("/write-data")
def write_data(user=Security(get_current_user, scopes=["write"])):
    return {"user": user, "wrote": True}
```

A token issued with `scopes: ["read"]` and presented to an endpoint requiring `scopes=["write"]` produces exactly the response this layering is built for:

```text
403 {"detail": "Not enough permissions, need write"}
```

`Security(...)`, used in place of `Depends(...)`, is what lets FastAPI thread each endpoint's own required scopes into `SecurityScopes`, which the dependency function receives alongside the token — the scopes are declared per-endpoint, at the route decorator, while the actual check happens once, in one shared dependency, per chapter 15's own composition pattern. This is exactly chapter 15's own dependency-graph mechanism, applied to a case chapter 15 did not itself cover: `Security` is `Depends` with one additional piece of per-call-site configuration — the required scopes — carried alongside the dependency callable itself, so `get_current_user` remains a single function serving every endpoint in the application, each endpoint simply asking it to enforce a different scope list. This is the concrete difference between **authentication** (the JWT's signature proves which user this is) and **authorization** (the scopes claim, checked separately, decides what that specific, already-authenticated user's token permits) — the same token, valid and correctly signed, can be entirely legitimate and still insufficient for a specific action.

### 2.8 The authorization code flow separates "the user proves who they are" from "the client receives a token," with the browser as an untrusted intermediary

The password grant, section 2.10's subject, has the client itself collect the user's actual username and password. The **authorization code flow** avoids this entirely: the client redirects the user's browser to the authorization server directly, the user authenticates there — on the authorization server's own page, never inside the client application — and the authorization server redirects back to the client with a short-lived, single-use authorization **code**, which the client then exchanges, in a separate, direct server-to-server call, for the actual token. The client application, at no point in this sequence, ever sees the user's password at all — the entire point of the extra redirect is keeping the credential confined to the one party that is actually supposed to verify it. **PKCE** (Proof Key for Code Exchange) adds one further protection to this flow: the client generates a random secret before the redirect, sends only a hashed version of it in the initial request, and must present the original secret when exchanging the code for a token — which stops an attacker who intercepts the authorization code alone (a real risk on a mobile device, where the redirect is an inter-app handoff rather than a same-process browser request) from completing the exchange without also having captured that earlier, separately-generated secret.

```mermaid
sequenceDiagram
    participant Client
    participant Browser
    participant AuthServer as Authorization Server
    Client->>Client: generate code_verifier (secret), derive code_challenge = hash(code_verifier)
    Client->>Browser: redirect to AuthServer with code_challenge
    Browser->>AuthServer: user authenticates directly with AuthServer
    AuthServer->>Browser: redirect back with a short-lived authorization code
    Browser->>Client: authorization code
    Client->>AuthServer: exchange code + code_verifier for a token
    AuthServer->>AuthServer: check hash(code_verifier) == code_challenge from earlier
    AuthServer->>Client: access token
```

The user's password is entered exactly once, on the authorization server's own page — the client application and the browser both handle only the authorization code, never the credential itself, and even the code is useless to an interceptor lacking the `code_verifier` only the original client ever generated.

### 2.9 OpenID Connect adds a standardized identity token on top of OAuth2's authorization mechanics

OAuth2, by itself, answers "is this request authorized" — it says nothing standardized about *who* the user actually is. **OpenID Connect (OIDC)** is a thin, standardized identity layer built directly on top of the authorization code flow section 2.8 already covers: alongside the ordinary access token, the authorization server also issues an **ID token** — itself a JWT, verified the same way sections 2.3 through 2.6 already describe — carrying standardized identity claims (`sub` for a stable user identifier, `email`, `name`, and others) that every OIDC-compliant provider agrees to populate the same way. This is what makes "log in with Google" or "log in with Microsoft" work identically across unrelated applications: the application never authenticates the user itself, never stores a password, and instead verifies one more JWT — the ID token — using the exact signature-checking discipline this chapter already builds, just against a public key the identity provider publishes rather than a secret the application's own backend holds. OIDC does not replace anything covered so far; it is OAuth2's authorization code flow, plus one additional, standardized token answering the identity question OAuth2 alone leaves unspecified.

### 2.10 OAuth 2.1 removes the password grant and the implicit grant entirely, and makes PKCE mandatory for every client

The pattern Tragura's own chapter presents as the standard solution — the client collecting a username and password directly and exchanging them for a token via `OAuth2PasswordRequestForm` — is the **Resource Owner Password Credentials grant**, and the OAuth 2.1 consolidation states its status without ambiguity: "The Resource Owner Password Credentials grant is omitted from this specification." The **Implicit grant** is removed on the identical terms. Both were live, standard parts of OAuth 2.0; neither exists in 2.1 at all.

```mermaid
graph TD
    subgraph old["OAuth 2.0"]
        PW["password grant — client collects<br/>username/password directly"]
        IMP["implicit grant — token returned<br/>directly in a redirect fragment"]
        AC1["authorization code — PKCE required<br/>only for public clients"]
    end
    subgraph new["OAuth 2.1"]
        REMOVED["password grant: removed<br/>implicit grant: removed"]
        AC2["authorization code — PKCE required<br/>for EVERY client, confidential included"]
    end
```

The password grant's fundamental problem was always structural, not merely old-fashioned: it requires the client application itself to handle the user's actual credential, which is precisely the trust boundary the authorization code flow exists to avoid crossing at all. OAuth 2.1's second major change compounds this — PKCE, previously recommended mainly for public clients unable to hold a secret safely, is now required for the authorization code flow **regardless of client type**, closing the same interception risk section 2.8 already describes for every integration, not only the ones historically considered most exposed. A book or tutorial presenting the password grant as a standard, current pattern is describing a grant type the specification governing current best practice has formally removed; this node's own currency correction is exactly that the password grant belongs in a codebase only as something to recognize and migrate away from, never as something to write into a new one.

---

## 3. Failure modes

### 3.1 Decoding a token without restricting `algorithms` trusts the token to declare its own verification method

```python
# Gist: unrestricted_algorithms.py
import jwt

token = jwt.encode({"sub": "alexandro"}, "some-secret", algorithm="HS256")
payload = jwt.decode(token, "some-secret", algorithms=["HS256", "HS384", "HS512", "none"])
```

Including `"none"` in an accepted-algorithms list — copied carelessly from an example, or left over from debugging — reopens exactly the vulnerability class section 2.6 already names: a token can present `alg: none` in its own header, requiring no signature verification at all, and a verifier willing to accept that algorithm as valid will accept a completely unsigned, freely-forgeable token as though it were genuine. This is not a hypothetical; unsigned or algorithm-confused tokens accepted by overly permissive verification code are a well-documented, recurring category of real JWT vulnerability. The fix is a hard rule rather than a case-by-case judgment call: `algorithms=[...]` should name exactly the one algorithm the server itself uses to sign tokens, and nothing else, ever — there is no legitimate reason for a verifier to accept more than the single algorithm its own issuance code actually produces.

### 3.2 Treating a JWT's payload as confidential leaks whatever was placed there, to anyone who ever sees the token

```python
# Gist: sensitive_payload.py
import jwt

token = jwt.encode(
    {"sub": "alexandro", "ssn": "123-45-6789", "role": "admin"},
    "some-secret", algorithm="HS256",
)
print(jwt.decode(token, options={"verify_signature": False}))
```

```text
{'sub': 'alexandro', 'ssn': '123-45-6789', 'role': 'admin'}
```

Section 2.3 already establishes why this succeeds with no key at all: a JWT's payload is base64, not encryption, and anything placed inside it — a social security number, an internal role name, an email address — is readable by the browser storing the token, by any logging system that happens to capture request headers, and by anyone who ever gains access to the token in transit or at rest, entirely independent of whether they possess the secret key needed to *forge* a new one. This is a genuinely common mistake specifically because a JWT looks opaque — a long string of apparently-random characters — to a developer who has not stopped to decode one by hand. The fix is treating the payload as no more protected than an unencrypted cookie: an identifier and a small amount of non-sensitive claim data (a user ID, a set of scopes) belongs there; anything a party without the secret key should not be able to read belongs in a database, looked up by the identifier the token does carry, never in the token itself.

### 3.3 Building new integrations against the password grant inherits a trust model OAuth 2.1 has already retired

```python
# Gist: new_password_grant_integration.py
@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # the client application itself collected form_data.password directly
    ...
```

`OAuth2PasswordRequestForm` still works, is still shipped by FastAPI, and still produces a functioning login endpoint — nothing about section 2.2's mechanism has been removed from the library, which is exactly what makes this trap easy to fall into for anyone learning FastAPI security from material written before the OAuth 2.1 consolidation, this node's own source among them. The endpoint runs correctly and the resulting API works exactly as documented; the problem is architectural rather than functional, and invisible from inside the code itself: every client integrating against this endpoint has to collect the user's actual password directly, which is precisely the trust boundary section 2.8's authorization code flow exists to avoid crossing, and precisely the pattern section 2.10's specification revision states plainly does not belong in current practice. A team building a new integration by copying this shape from an older tutorial inherits that trust model without ever making an explicit decision to accept it. The fix is not a code change to the password-grant endpoint itself — it is choosing the authorization code flow with mandatory PKCE for any new integration, and treating `OAuth2PasswordRequestForm` as a pattern to recognize in an inherited codebase, never one to reach for when writing something new.

### 3.4 A short or guessable signing key undermines the signature guarantee the entire scheme depends on

```python
# Gist: weak_signing_key.py
import jwt
jwt.encode({"sub": "alexandro"}, "short", algorithm="HS256")
```

```text
InsecureKeyLengthWarning: The HMAC key is 5 bytes long, which is below the minimum
recommended length of 32 bytes for SHA256. See RFC 7518 Section 3.2.
```

`PyJWT` itself warns about this, by name, citing the specific RFC section that recommends a minimum key length — a genuinely different failure mode from every other one in this chapter, because nothing here is about a mistake in how the token is *used*; it is about the strength of the one secret every guarantee in sections 2.3 through 2.6 ultimately rests on. `HS256`'s security is entirely a function of how hard the key is to guess or brute-force; a five-byte key is short enough that an attacker attempting to forge tokens does not need to break the HMAC algorithm at all, only search a small enough key space to find it directly, at which point every guarantee this chapter has built up — tamper detection, expiration enforcement, scope restriction — is available to forge freely, because the attacker can simply mint their own validly-signed tokens claiming to be anyone, with any scopes they choose. The fix is generating a genuinely random key of adequate length — the `openssl rand -hex 32` invocation this node's own migration source already demonstrates produces a 32-byte value appropriate for `HS256` — and storing it as deployment configuration, never a literal string typed into source code, which is a separate and equally real risk this same warning does nothing to catch.

---

## 4. Trade-offs

| Approach | Use when | Because | Real cost |
| --- | --- | --- | --- |
| **HTTP Basic** | The simplest possible internal tooling, always behind TLS, never exposed to untrusted networks | Zero setup — no token issuance, no signing key to manage | Sends the real credential on every request; no scoping, no expiration, no revocation short of changing the password |
| **Password grant (legacy)** | Recognizing and migrating an inherited codebase | N/A — OAuth 2.1 has removed it; there is no case where this is the right choice for new work | Requires the client to handle the user's real credential directly, the exact trust boundary current best practice avoids |
| **Authorization code flow with PKCE** | Any new integration, browser-based or native, confidential client or public | The client never sees the user's credential; PKCE closes the code-interception gap for every client type under OAuth 2.1 | More moving parts — a redirect, a code exchange, PKCE's own extra round trip — than a direct password exchange |
| **JWT, short expiration + refresh token** | Stateless verification is worth more than instant revocability | No database lookup needed to validate a request | A leaked token remains valid, in full, until it expires — there is no way to revoke one early without added infrastructure |
| **Opaque session token, database-backed** | Instant revocation matters more than avoiding a lookup | Deleting the server-side record invalidates the token immediately | Every request now needs a database round trip purely to check validity |
| **OpenID Connect via an external provider** | The application should never store or handle a user's actual password at all | Identity verification is fully delegated; a data breach of the application cannot expose credentials it never held | A hard runtime dependency on the identity provider's own availability, and integration complexity beyond a self-issued token |
| **A self-issued token with no external identity provider** | The application is the sole authority over its own users, with no need to federate identity anywhere else | No third-party dependency, full control over the token's contents and lifecycle | The application itself becomes the thing responsible for storing credentials securely — and the thing attacked if it fails to |

### The case against building a custom identity system when an OIDC provider is available

A hand-rolled username/password/reset-flow system is a genuine, ongoing security surface — password hashing choices, reset-token generation, account-enumeration prevention on the login form itself, breach-detection for reused credentials — none of which is specific to any one application's actual business logic, and all of which a mature OIDC provider has already solved, audited, and hardened against real attacks at a scale no single application's own security review is likely to match. The rejected alternative to delegating identity is treating "we control the whole stack" as inherently more secure, when in practice it usually means reimplementing a well-understood, high-stakes problem from scratch, under less scrutiny than the specialized providers built to solve exactly that problem receive. Building a custom system remains the right choice specifically when the application's own users are not naturally represented by any external identity provider at all — an internal system with a fixed, small set of accounts an operations team provisions directly, where federating identity externally would add a dependency with no corresponding benefit.

### The case against JWTs for anything requiring instant revocation

A JWT's entire value proposition — verify without a lookup — is also its sharpest limitation: there is no way to invalidate one early short of maintaining a server-side blocklist, which reintroduces the exact database dependency the token was chosen to avoid in the first place. The rejected alternative to a pure JWT here, for a system where "revoke this session right now" is a real requirement (a compromised account, a forced logout), is either a short enough expiration that the exposure window is acceptable on its own, or a hybrid design — a JWT for ordinary request validation, checked against a small, fast revocation list for the rare case something needs to be killed before its natural expiry — rather than pretending a stateless token can offer a guarantee it structurally cannot.

---

## 5. Reference summary

**HTTP Basic sends the real credential, base64-encoded — not encrypted — on every request**, which is why it depends entirely on TLS for any real security and has fallen out of favor beyond simple internal tooling. **`OAuth2PasswordBearer` is an ordinary `Depends()`-compatible callable** extracting a bearer token from the request header; it validates nothing about the token's contents on its own.

**A JWT's three segments are base64url-encoded, not encrypted — the payload is readable by anyone holding the token, with or without the signing key.** **The signature is what makes a JWT trustworthy**: it proves the content has not been altered since issuance, and proves nothing about who may read it, which is why sensitive data never belongs in a token's payload. **`exp` is an ordinary payload claim, enforced by the verifying library as a separate check from signature validation** — a token past its expiration still carries a perfectly valid signature. **A verifier must explicitly restrict accepted algorithms (`algorithms=[...]`)**, never trusting the `alg` field a token's own header claims, because algorithm-confusion and `alg: none` attacks are a well-documented, real vulnerability class in JWT libraries that once trusted that field blindly. **A refresh token, issued alongside a short-lived access token and presented only to a dedicated refresh endpoint, splits exposure risk in two** — a leaked access token is dangerous briefly; a leaked refresh token is dangerous longer but is transmitted far less often, to a narrower surface.

**Scope-based authorization layers "what this token permits" on top of "whose token this is"** — the same validly-signed, correctly-issued token can be legitimate and still insufficient for a specific action, checked via FastAPI's `Security()`/`SecurityScopes`, which threads each endpoint's required scopes into one shared authentication dependency.

**The authorization code flow keeps the client application from ever seeing the user's actual credential**, redirecting authentication to the authorization server directly and exchanging a short-lived code for a token in a separate, direct call; **PKCE** adds a client-generated secret, hashed in the initial request and required again at exchange time, closing the risk of an intercepted authorization code being redeemed by anyone other than the client that requested it.

**OpenID Connect adds a standardized identity token — itself a JWT, verified the same way — on top of OAuth2's authorization code flow**, which is what lets an application delegate identity verification to an external provider entirely, never storing or handling a password of its own.

**OAuth 2.1 removes both the Resource Owner Password Credentials grant and the Implicit grant entirely**, and **makes PKCE mandatory for the authorization code flow for every client type**, not merely public clients as under OAuth 2.0. A 2022-era tutorial presenting the password grant as a standard pattern is teaching a grant type current best practice has formally retired — legitimate to recognize in an inherited codebase, never to write into a new one.

---

← [Python knowledge graph](00_knowledge_graph.md) · [repo index](../README.md)
