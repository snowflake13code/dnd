# Repository review notes

## Local changes

- Replaced the minimal README with source-verified architecture, a Mermaid diagram, setup, synthetic examples, format requirements, and limitations.
- Added five original fictional notes in `examples/notes` covering characters, a player, structures, two session scenes, aliases-compatible wikilinks, and a session reference. They are unrelated to the existing campaign personas.
- Added `.env.example`; `NOTES_LOCATION` and `DATABASE_LOCATION` now allow separate sample input/storage while retaining original fallback paths. Configuration loads `.env` before opening stores.
- Fixed ingestion imports so both module and legacy script entry points work, moved graph initialization into the command entry point, and added a missing-notes-directory check.
- Pinned directly used packages to locally installed versions, declared `langchain-core` explicitly, and replaced the `dotenv` wrapper with `python-dotenv`. No unused umbrella `langchain` dependency is needed by current imports.
- Expanded ignore rules for local environments, configuration, private notes, caches, and generated storage.

## Verification performed

Checked using the existing Python 3.13.14 environment:

- `python -m compileall -q app.py src`: passed.
- `python -m pip check`: passed; no broken installed requirements.
- `git diff --check`: passed.
- Temporary isolated synthetic smoke test using fixed test embeddings and real Chroma/Kùzu: passed. Verified six documents (four note documents and two scene documents), latest arc/session state, session-reference ghost resolution, chronological session/arc retrieval, and story retrieval with graph expansion. Fixed embeddings validate plumbing, not semantic retrieval quality.
- `NOTES_LOCATION=./examples/notes DATABASE_LOCATION=./database/example-smoke .venv/bin/python -m src.obsidian_reader`: passed against the installed local Ollama service and `mxbai-embed-large` model. Generated files remain ignored and separate from the original database paths.

Not verified: a fresh dependency installation, other Python versions/platforms, live Groq routing or generation, browser UI interaction, retrieval quality, or performance. No screenshot was captured. A working local environment does not establish reproducibility on every fresh machine.

## Security and privacy review

Current tracked files contain no `.env`, databases, logs, or note vault. The existing local `.env` was not printed, changed, or used to call Groq. No personal vault was read or indexed.

Git history contains generated databases, vector indexes, logs, and compiled Python files. The owner confirmed that the historical databases and logs contain test data and are acceptable to retain publicly. No history cleanup is requested or needed for this review. History remains unchanged.

A local heuristic scan of all 132 reachable Git objects checked recognizable Groq/OpenAI/GitHub/Stripe token prefixes, AWS access-key identifiers, and private-key headers; it found no matches. No dedicated secret scanner was installed. This limited scan does not rule out unrecognized credentials or sensitive prose. If further review finds a credential, revoke/rotate it even if it is subsequently removed from history.

The committed persona prompts retain existing campaign-specific names and setting details. The sample uses the generic `assistant` persona to avoid mixing those identities into its example.

## Suggested GitHub About settings

Description:

> Graph-aware RAG assistant for Obsidian D&D notes, combining semantic search, linked-note expansion, and LLM routing in Streamlit.

Topics:

`rag`, `retrieval-augmented-generation`, `knowledge-graph`, `python`, `obsidian`, `streamlit`, `chromadb`, `kuzu`

Owner steps: open the repository on GitHub, click the gear beside **About**, paste the description, add the topics, and save. These are proposals only; remote settings were not changed.
