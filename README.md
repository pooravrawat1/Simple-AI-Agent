# Simple AI Agent

Lightweight interactive CLI agent that uses LangChain, LangGraph and MCP tools to create a ReAct-style agent powered by OpenAI models and Firecrawl web-crawling tools.

## Project specification

- Purpose: provide an interactive command-line assistant that can use external MCP-compatible tools (for example Firecrawl) to scrape and extract information from web pages and combine that with a language model to answer user questions.
- Primary interface: `main.py` — an asyncio-based CLI loop that loads MCP tools, builds a ReAct agent and accepts user prompts.
- Inputs: interactive user text (via stdin). Environment variables for API keys:
	- `OPENAI_API_KEY` — OpenAI API key used by `langchain_openai.ChatOpenAI`.
	- `FIRECRAWL_API_KEY` — API key used by the Firecrawl MCP server invoked via `npx firecrawl-mcp`.
- Outputs: printed agent responses to stdout; the agent may call MCP tools to fetch, crawl, or extract web data.
- Runtime: Python >= 3.11, uses asyncio for concurrency and `npx` (Node.js) to launch the Firecrawl MCP process.

Design/behavior notes:
- The agent is created via `langgraph.prebuilt.create_react_agent` which implements the ReAct pattern (reasoning + acting via tools).
- Tools are dynamically loaded with `langchain_mcp_adapters.tools.load_mcp_tools` from an MCP session established with a `stdio` client.
- The OpenAI model used in `main.py` is `gpt-4o-mini` (configured via the `ChatOpenAI` wrapper) with deterministic temperature (0).
- The code prints available tools, starts an interactive loop and forwards user messages to the agent. Typing `quit` exits.

## Key technologies used

- Python (>= 3.11)
- Asyncio — asynchronous event loop and concurrency.
- LangChain ecosystem:
	- `langchain-mcp-adapters` — adapter for MCP tools
	- `langchain-openai` — OpenAI model adapter
	- `langchain-core` (pulled in by dependencies)
- LangGraph (`langgraph`, `langgraph-prebuilt`, `langgraph-sdk`) — provides prebuilt agent patterns and orchestration (ReAct agent creation)
- MCP (`mcp`) and MCP stdio client — Model/Tool Connector Protocol used to call external tools
- Firecrawl (external Node.js tool invoked via `npx firecrawl-mcp`) — web crawling/scraping tools surfaced to the agent through MCP
- OpenAI — model provider (uses an API key via `OPENAI_API_KEY`)
- python-dotenv — load environment variables from a `.env` file
- Node.js / npm (required to run Firecrawl via `npx`)

Additional (transitive) packages (found in `uv.lock`): httpx, httpcore, pydantic, jsonschema, anyio and many others used by the LangChain/LangGraph stack.

## Files of interest

- `main.py` — the interactive entrypoint. Key responsibilities:
	- Loads environment variables with `python-dotenv`.
	- Creates an OpenAI model instance via `ChatOpenAI`.
	- Starts an MCP stdio client using `npx firecrawl-mcp` and loads available tools.
	- Builds a ReAct agent via `create_react_agent` and runs an interactive CLI loop.
- `pyproject.toml` — declares project metadata and main Python dependencies (`langchain-mcp-adapters`, `langchain-openai`, `langgraph`, `python-dotenv`).
- `uv.lock` — lockfile listing resolved dependency versions for reproducible installs.

## Quickstart

Prerequisites
- Python 3.11 or newer
- Node.js and npm (for `npx` / Firecrawl)
- An OpenAI API key and (if you intend to use Firecrawl) a Firecrawl API key

Environment
1. Copy or create a `.env` file in the project root with the following keys:

```bash
OPENAI_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
```

Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
# Install the core packages declared in the project
pip install langchain-mcp-adapters langchain-openai langgraph python-dotenv
```

Note: `uv.lock` contains a fully resolved dependency graph. If you use a dependency manager (pip-tools, poetry, or the tool that produced `uv.lock`), prefer installing using that lockfile for exact versions.

Firecrawl (if you want web crawling tools)

```bash
# Firecrawl is started by the code via npx. Ensure npm/node is installed.
# You can also test running the MCP server manually:
npx firecrawl-mcp
```

Run the agent

```bash
# Standard: run the main entrypoint directly
python main.py

# Alternative: if you use 'uv' as a task runner you can start the project with:
uv python main.py
```

Usage
- After starting, the program will list available tools and prompt with `You>`.
- Ask questions or give commands. The agent may call the Firecrawl tools (if available) to fetch or crawl pages.
- Type `quit` to exit.

## Expected inputs/outputs and error modes

- Inputs: free-text user prompts (stdin). Long inputs are truncated to a safe size in `main.py`.
- Outputs: the agent's reply printed to stdout. If an exception occurs, the code prints `Error:` followed by the exception.
- Common failure modes:
	- Missing environment variables (`OPENAI_API_KEY`, `FIRECRAWL_API_KEY`) — agent will fail to construct or call external services.
	- `npx` / Node.js not installed — MCP stdio client cannot start Firecrawl.
	- Network connectivity or API quota errors from OpenAI / Firecrawl.

## Security & privacy
- Do not commit `.env` files containing API keys. Add them to `.gitignore`.
- Be mindful that web scraping tools may collect personal data; follow legal and ethical guidelines.

## Next steps / ideas
- Add a `requirements.txt` or provide a `poetry`/`pip` lockfile for easier installs.
- Add command-line flags to `main.py` for non-interactive runs (e.g., `--prompt` to run a single prompt and exit).
- Add tests for the agent initialization and tool-loading code paths using local mocks for the MCP server.

## Development notes
- The code uses `asyncio.run(main())` in the `__main__` block and expects an MCP process reachable over stdio.
- To customize the OpenAI model or temperature, edit the `ChatOpenAI(...)` constructor in `main.py`.

---

If you'd like, I can:
- add a `.env.example` file,
- create a simple `requirements.txt` extracted from `uv.lock`, or
- add a non-interactive script wrapper for automated queries.

