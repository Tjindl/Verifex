# AI Code Explainer

A production-quality developer tool that explains **WHY** a piece of code is correct, focusing on logical properties like invariants, termination, and complexity, rather than just what it does.

## Architecture

The system uses a hybrid Neuro-Symbolic approach:
1.  **Static Analysis (Core)**: 
    - Uses `tree-sitter` to parse Python code into an AST.
    - Deterministically extracts Control Flow, Loops, Recursion, and Variable roles.
    - Applies heuristics to identify candidates for Invariants (e.g. range bounds).
2.  **LLM Reasoning (Reasoning)**:
    - Takes the structured metadata from the Core module.
    - A formal verification persona (System Prompt) generates the logical explanation.
    - Output is strictly structured JSON.

## Project Structure

```
code_explainer/
├── main.py                 # FastAPI Entry Point
├── core/
│   ├── analyzer.py         # Orchestrator
│   ├── parser.py           # Tree-sitter Wrapper
│   ├── heuristics.py       # Invariant Detection
│   └── models.py           # Pydantic Models
├── llm/
│   ├── client.py           # OpenAI Client (with Mock fallback)
│   └── prompts.py          # Prompt Templates
└── api/
    └── routes.py           # API Endpoints
```

## Setup & Usage

### Running the Application (Full Stack)
The easiest way to run the full stack (Frontend + Backend) is with Docker:

```bash
export GEMINI_API_KEY="your_key"
make docker-build
make docker-run
```
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs

### Local Development
**Backend**:
```bash
make backend-install
make backend-serve
```
**Frontend**:
```bash
make frontend-install
make frontend-dev
```

## Architecture
The project is a monorepo with the following structure:
- `backend/`: FastAPI application (Python)
    - `code_explainer/`: Core logic (Tree-sitter + Gemini)
- `frontend/`: Next.js application (React)
    - `app/`: App Router pages
    - `components/`: Shadcn UI components

## Design Decisions
- **Next.js & Shadcn UI**: We chose a modern React stack for a premium, responsive user experience.
- **Monorepo**: Keeping frontend and backend together simplifies versioning and deployment.
- **Docker Compose**: Orchestrates both services with a single command.
- **Hybrid Analysis**: We combine deterministic static analysis (backend) with LLM reasoning (backend) and visualize it beautifully (frontend).
- **Gemini Integration**: We use the latest `google-genai` SDK for high-performance and future-proof inference.