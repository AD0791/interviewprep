# Use Case: Highly Performant CORS & Compression Stack for FastAPI
# Purpose: Compresses payloads to reduce response sizes and caches CORS preflight checks.
# Key features: GZipMiddleware, CORSMiddleware with preflight max_age caching.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# 1. Enable Compression Middleware
# Why: Brotli/Gzip reduces transmission latency of large aggregated JSON payloads
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB

# 2. CORS Middleware Configuration
# Why: Authorizes React connections while caching browser OPTIONS queries to eliminate preflight lags
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",          # Local React dev server
        "https://dashboard.company.com"   # Production server url
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Tenant-ID"],
    # Access-Control-Max-Age: 600 (Cache preflight options checks in browser for 10 minutes)
    max_age=600, 
)
