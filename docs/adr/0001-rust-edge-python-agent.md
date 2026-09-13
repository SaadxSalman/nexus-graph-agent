# ADR 0001: Rust Edge and Python Agent

## Status

Accepted

## Context

The public service needs a small compiled boundary, while LangGraph, model SDKs, and retrieval experimentation are most mature in Python.

## Decision

Use Rust for browser delivery, forwarding, and edge-level request handling. Use Python for orchestration, model providers, retrieval adapters, MCP, and evaluation.

## Consequences

The repository has two build systems and two runtime processes. The boundary is explicit and testable. Python can evolve the agent without expanding the public edge attack surface. Docker Compose and CI must validate both languages.
