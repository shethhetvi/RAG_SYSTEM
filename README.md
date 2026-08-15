# Voice-Enabled RAG System

This project is built for the **HH Goa 2026 Shortlisting Task 2: Build a Voice-Enabled RAG Model**.

## Overview
A voice-enabled Retrieval-Augmented Generation (RAG) system that transcribes a user's spoken question, retrieves relevant context from the provided MSMARCO-XI dataset, and returns an answer end-to-end within a strict 200ms latency target.

## Project Structure
- `backend/`: Python API (FastAPI) for ML pipeline, chunking, retrieval, and generation.
- `frontend/`: Web interface for voice input and answer display.

## Key Requirements Implemented
1. **Speech-to-Text**: Utilizing Sarvam or ElevenLabs.
2. **Chunking**: Advanced chunking strategies for retrieval.
3. **Latency**: End-to-end execution under 200ms.
4. **Harness & Guardrails**: Structured model orchestration with checks for off-topic or unsafe queries.

## Getting Started
(Add setup instructions here)
