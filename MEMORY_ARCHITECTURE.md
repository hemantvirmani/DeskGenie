# DeskGenie Memory Architecture Plan

## Background

DeskGenie currently runs each agent invocation as a cold start — no history from the
current chat session or past sessions is passed to the agent. The chat JSON files on
disk contain everything needed; they are just never used at inference time.

This document defines a two-layer memory system (plus short-term context) to fix that.

---

## The Memory Types

| Type | What it stores | Analogy | Retrieval |
|---|---|---|---|
| **Short-term** | Last N messages from the current chat session | Working memory | Always-on — loaded from existing chat JSON |
| **Episodic** | Specific past interactions — what happened, when, in which chat | Your diary | Similarity search via ChromaDB |
| **Semantic** | Distilled facts about the user — preferences, patterns, corrections | Your mental model of a person | Always-on — entire file injected into every prompt |
| ~~**Procedural**~~ | ~~Successful tool chains~~ | ~~Muscle memory~~ | *Not needed — see note below* |

### Why procedural memory is out of scope

Storing and replaying tool chains adds complexity for marginal gain. Gemini 2.5 Flash
already rediscovers good sequences reliably, and tool chains vary too much by context
(different paths, file types, intent) to be usefully reusable. Dropped for now; if
empirical evidence shows repeated rediscovery failures, revisit.

### Why the two active types are distinct

Episodic memory stores raw events with temporal context — the exact question, answer,
and tools used in a specific past session. Over time, the specific episode becomes less
relevant but the fact it revealed persists. That distillation process — episode → durable
fact — is what creates semantic memory. You do not remember the moment you learned that
Paris is the capital of France; the episode got discarded, the fact remained.

---

## Storage Decisions

```
Short-term              ──► Existing chat JSON   (last N message pairs, no new infra)
Episodic                ──► ChromaDB             (similarity retrieval across past Q&As)
Semantic                ──► semantic_memory.md   (plain markdown, injected whole, like CLAUDE.md)
```

**Rule of thumb**: If you need "find me something *similar*", it is a ChromaDB job.
If you need "tell the agent everything it should always know", it is a markdown file.

### Embedding model

ChromaDB's built-in default embedding function — an ONNX version of `all-MiniLM-L6-v2`,
downloaded automatically to a local cache on first use (~22 MB). No API key required,
works offline, provider-agnostic. Switching the chat LLM to kimi, Ollama, or anything
else has no effect on embeddings.

**No `sentence-transformers` package.** ChromaDB handles the model download internally.

---

## Storage Layout

```
%LOCALAPPDATA%\DeskGenie\memory\
  chroma/              ← ChromaDB persistent store (episodic collection)
  semantic_memory.md   ← plain markdown facts, edited by distiller or by hand
```

`semantic_memory.md` format (like CLAUDE.md — human-readable, manually editable):

```markdown
# What I know about you

- Prefers output files saved to ~/Downloads
- Frequently works with PDFs and design assets
- Uses the alias 'designs' for ~/Projects/Client-X/assets/
- Corrected me when I used ~/Documents instead of ~/Downloads
```

---

## Full Data Flow

```
User sends message in chat topic "PDF experiments"
               │
               ▼
      ┌─────────────────┐
      │  genie_api.py   │  receives: message + chat_id + file_name
      └────────┬────────┘
               │
               ▼
      ┌─────────────────────────────────────────────────────┐
      │              memory_manager.py                       │
      │                                                       │
      │  1. Load current chat JSON → last N messages         │  ← short-term (no DB)
      │  2. Query episodic store  → top-3 similar past Q&As │  ← ChromaDB
      │  3. Read semantic_memory.md → inject all facts       │  ← plain markdown
      └────────────────────────┬────────────────────────────┘
                               │
                               ▼
      ┌─────────────────────────────────────────────────────┐
      │         langgraphagent.py  _init_questions()         │
      │                                                       │
      │  SystemMessage(                                       │
      │    base_system_prompt                                 │
      │    + ## What I know about you   (semantic_memory.md) │
      │    + ## Relevant past context   (episodic top-3)     │
      │  )                                                    │
      │  HumanMessage(prior turn 1)   ← current chat history │
      │  AIMessage(prior answer 1)                           │
      │  HumanMessage(prior turn 2)                          │
      │  AIMessage(prior answer 2)                           │
      │  HumanMessage(current question)                      │
      └─────────────────────────────────────────────────────┘
               │
               ▼
         Agent runs, produces answer
               │
               ▼
      ┌─────────────────────────────────────────────────────┐
      │              Post-run indexing                        │
      │                                                       │
      │  1. save_chat()       → persists JSON (existing)    │
      │  2. index_episode()   → write Q&A to ChromaDB       │
      │  3. distill_semantics() → every N queries, sync,    │
      │                           uses active LLM provider,  │
      │                           rewrites semantic_memory.md│
      └─────────────────────────────────────────────────────┘
```

### Distillation trigger

Distillation runs **synchronously after the Nth query** (not in the background).
The user experiences a slightly longer response on that turn. N is configurable
(`memory.semantic.distillationEveryN`, default 5). The active LLM provider
(whatever is set in `config.json → llm.activeProvider`) runs the distillation call —
no second API key required, no Google lock-in.

---

## What Each Memory Contains

### Episodic — ChromaDB collection: `episodic`

One document per Q&A exchange.

```python
{
  "id":       "chat_abc_msg_4",
  "text":     "Q: How do I convert my PDF to images?\nA: Used pdf_to_images tool, saved to ~/Downloads",
  "metadata": {
    "chat_id":    "abc",
    "chat_name":  "PDF experiments",
    "timestamp":  1746123456,
    "msg_index":  4,
    "has_file":   True,
    "tools_used": ["pdf_to_images"]
  }
}
```

Retrieved by similarity to the current question. Top-3 results above a threshold are
injected into the prompt as a `## Relevant past context` block.

---

### Semantic — `semantic_memory.md`

Plain markdown bullet list. Written by the distiller, readable and editable by hand.
The entire file is injected into every prompt — no search, no threshold, no retrieval
logic. If the file grows unwieldy the distiller is responsible for deduplication and
pruning on each rewrite.

---

### Procedural — *not implemented*

Placeholder. Storing and replaying tool chains was evaluated and dropped (see note
above). The section is kept here so the decision is visible and reversible.

---

## Prompt Structure at Runtime

```
[Base system prompt — existing, unchanged]

## What I know about you
- You prefer output files saved to ~/Downloads
- You frequently work with PDFs and design files
- You use the alias 'designs' for ~/Projects/Client-X/assets/
- You corrected me when I used ~/Documents instead of ~/Downloads (2 weeks ago)

## Relevant past context
[April 3 — "PDF experiments" chat]
Q: How do I extract the last 3 pages of a report?
A: Used pdf_extract_pages with range "last3", saved to ~/Downloads/report_extract.pdf

[March 28 — "Client work" chat]
Q: Convert all PDFs in the designs folder to images
A: Used pdf_to_images on each file, saved as PNG to ~/Downloads
```

Followed by the current chat history as alternating `HumanMessage` / `AIMessage` turns,
then the current question as the final `HumanMessage`.

---

## New Files

```
utils/
  memory/
    __init__.py        — exports MemoryManager
    chroma_client.py   — shared persistent ChromaDB client (one instance, episodic collection)
    episodic.py        — index_episode(), retrieve_similar_episodes()
    semantic.py        — read_semantic_memory(), write_semantic_memory()
    manager.py         — MemoryManager: orchestrates episodic + semantic + distillation trigger
    distiller.py       — LLM call to extract/rewrite semantic facts from recent episodes
    backfill.py        — one-time script to index all existing chat JSON files into ChromaDB
```

---

## Changes to Existing Files

| File | Change |
|---|---|
| `app/genie_api.py:80` | Add `chat_id: Optional[str]` to `ChatRequest` |
| `app/genie_api.py:149` | Call `MemoryManager.build_context(question, chat_id)` before invoking agent; call `MemoryManager.post_run_index(...)` after |
| `agents/langgraphagent.py:142` | `_init_questions` accepts `memory_context` dict and `chat_history` list; assembles full message list |
| `agents/langgraphagent.py:308` | `__call__` accepts `chat_history` and `memory_context` kwargs, passes them to `_init_questions` |
| `agents/agents.py:23` | `__call__` passes through `chat_history` and `memory_context` |
| `utils/chat_storage.py:56` | `save_chat` triggers `MemoryManager.on_chat_saved(chat)` after writing to disk |
| `utils/data_dir.py` | Add `get_memory_dir()` → `%LOCALAPPDATA%\DeskGenie\memory\` |
| `config.json.example` | Add `memory` section (see below) |

---

## Config Additions (`config.json`)

```json
"memory": {
  "enabled": true,
  "currentChatMaxMessages": 6,
  "episodic": {
    "enabled": true,
    "topK": 3,
    "similarityThreshold": 0.72
  },
  "semantic": {
    "enabled": true,
    "distillationEveryN": 5
  }
}
```

`currentChatMaxMessages: 6` means 3 prior Q&A pairs. `distillationEveryN: 5` means
the semantic facts file is rewritten after every 5 queries.

---

## Dependencies to Add

```
chromadb    # embedded vector store + built-in ONNX embeddings (~22 MB cached on first use)
```

One new dependency. No `sentence-transformers`. No API key for embeddings.

---

## Phased Implementation

### Phase 1 — Current chat context (no new dependencies)

**Goal**: Agent maintains coherence within a session. "Sort them by date" after "list my
files" works without re-stating context.

1. Add `chat_id: Optional[str]` to `ChatRequest`
2. In `run_agent_task`, load the chat JSON and extract the last N message pairs
3. Pass the list into `LangGraphAgent.__call__`
4. In `_init_questions`, prepend the prior turns as alternating `HumanMessage` / `AIMessage`
   before the current question

No new dependencies. No vector DB. Pure JSON reads from existing chat files.

#### Design decision — chat_id ownership

`chat_id` is a session identifier, not frontend intelligence. The frontend passes
it because it knows which conversation the user is looking at; all reasoning about
what to do with it (load history, inject into prompts) is entirely backend.

Programmatic callers (CLI, scheduled tasks) have no frontend to supply `chat_id`.
The fix for those callers is not to remove `chat_id` from the API, but to have
the backend create the chat group and return its ID at task-creation time so the
caller can pass it explicitly. See the Scheduled Tasks section for the full design.

---

### Phase 2 — Episodic memory

**Goal**: Agent recalls similar situations from any past session, not just the current one.

1. Add `chromadb` to `requirements.txt`
2. Create `utils/memory/` skeleton — `chroma_client.py`, `episodic.py`, `manager.py`
3. Hook `save_chat` → `MemoryManager.on_chat_saved()` → `index_episode()`
4. Run `backfill.py` once to index all existing chat files
5. In `run_agent_task`, call `retrieve_similar_episodes(question)` and inject results

---

### Phase 3 — Semantic memory

**Goal**: Agent behaves like it knows the user personally — applies preferences
proactively without being told.

1. Implement `semantic.py` (file read/write) and `distiller.py` (LLM call)
2. Distillation triggered synchronously after every N queries in `post_run_index()`
3. Uses whatever active LLM provider is configured — no hardcoded model
4. Distiller prompt instructs the LLM to: read recent episodes, extract durable facts,
   merge with existing `semantic_memory.md`, deduplicate, rewrite the file
5. Hard preferences remain in `config.json → preferences` (already exists)

---

### Phase 4 — Procedural memory (deferred / not planned)

Not implemented. Revisit only if there is empirical evidence that the agent repeatedly
fails to rediscover working tool chains for common task types.

---

## Guardrails

Memory has direct access to the system prompt. Bad data corrupts every subsequent
response. Three vectors, three sets of guardrails.

---

### Vector 1 — Bad episodes indexed (Episodic)

A failed run stored in ChromaDB gets retrieved as "relevant past context" and poisons
future answers.

| Guardrail | Implementation |
| --- | --- |
| Only index successful runs | Skip indexing if answer is an error string or `step_count < 1` |
| Similarity threshold | Already 0.72 — do not lower it |
| Hard injection cap | Top-3 episodes maximum, never more |

---

### Vector 2 — Semantic facts drift or contradict

The distiller is an LLM call. It can hallucinate facts, promote one-off events to
permanent preferences, or produce contradictions in the same file.

| Guardrail | Implementation |
| --- | --- |
| Rewrite, never append | Distiller rewrites the entire `semantic_memory.md` each pass — deduplication and contradiction resolution are built in |
| Minimum episode support | Distiller prompt: only extract facts seen in **2+ episodes**, not one-offs |
| Hedged language | Distiller prompt enforces: "tends to", "often", "prefers" — never "always" or "never" |
| Hard fact cap | Maximum 25 facts in the file; distiller must prune when over the limit |
| No absolute paths | Paths go stale; store folder alias names (`designs`, `work`) not full paths |
| Human override | Plain markdown — user can open and manually delete wrong facts at any time |

---

### Vector 3 — Correct memory injected in the wrong frame

Even accurate memories confuse the agent if presented as ground truth rather than hints.

| Guardrail | Implementation |
| --- | --- |
| Hedged section headers | `## Past context that may be relevant` not `## What happened` |
| Hedged semantic header | `## What I generally know about you` not `## Facts about you` |
| Short-term cap | 6 messages (3 Q&A pairs) maximum — stale turns from the same session add noise |
| Only successful turns in short-term | Skip error turns when loading chat history |

---

### System-level guardrails

| Guardrail | Implementation |
| --- | --- |
| Kill switch | `memory.enabled: false` in `config.json` — turns off all memory instantly |
| Graceful degradation | ChromaDB errors are caught and logged; agent continues without episodic context rather than crashing |
| `/clear-episodic` command | Wipes the ChromaDB episodic collection only — semantic facts are preserved |
| `/clear-semantic` command | Deletes `semantic_memory.md` only — episodic history is preserved |
| `/clear-memory` command | Does both — full reset, agent starts completely fresh |

---

### The single most important guardrail

**The distiller rewrites, never appends.** An append-only semantic file accumulates
contradictions and bloat across every distillation pass. A full rewrite forces the LLM
to reconcile everything, stay under the fact cap, and drop stale or conflicting entries.
The plain markdown format makes every rewrite inspectable and manually correctable.

---

## Recommended Start

Begin with **Phase 1**. It delivers the highest day-to-day value (session coherence)
with no new dependencies. Phase 2 adds cross-session recall. Phase 3 adds the
"agent knows you" layer on top of the same infrastructure.

---

## Future: Scheduled Tasks

Scheduled tasks (agent runs triggered on a schedule, without the UI open) have
two requirements the current CLI `--query` path does not satisfy:

1. **Persistence** — results must be written to a chat group so the user can
   review what ran when they next open the UI.
2. **Context** — each run should see what the previous run of the same task did,
   using Phase 1 history injection.

### Design

Each scheduled task type gets a **dedicated chat group** (e.g. "Weekly folder
cleanup", "Daily email summary"). Each run appends its Q&A to that group. The
user opens the UI and sees the full history of past runs in the sidebar.

### What needs to change

The current `run_agent_task` in `app/genie_api.py` has no concept of saving
results — saving is done by the frontend after polling. Headless runs have no
frontend, so `run_agent_task` needs a `save_result: bool = False` flag path
that calls `save_chat()` directly after the agent returns.

`_extract_chat_history` already accepts a `chat_id` — a scheduled task passes
its dedicated group's ID, and automatically gets the last N prior runs as
context. No new memory infrastructure needed.

### What to avoid

Do **not** reuse the CLI `--query` path for scheduled tasks. It is intentionally
ephemeral (no persistence, no chat group) and suits one-shot scripting and CI
smoke tests. Scheduled tasks are a different contract: persistent, reviewable,
and context-aware.
