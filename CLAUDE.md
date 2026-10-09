
# CLAUDE.md

Project instructions. Read before writing code in this repository.

## What this is

Kamdonthi — an agentic advisory assistant for a district extension office in Mulanje, Malawi. It drafts climate-smart planting and spraying advisories from rainfall, pest and plot records, cites the record behind every recommendation, and stops for a named officer to approve.

Built for the African Agentic AI Design Challenge, Agriculture track. **Submission closes 15 October 2026.** Repositories are cloned at the deadline and later commits disqualify the entry.

## Hard rules

These are disqualification lines in the challenge rules. Never write code that breaks one, and raise it if an instruction would.

1. **The agent never sends.** It drafts and queues. Release requires a named approver recorded in the queue. There is no code path — not a flag, not a test helper, not a debug mode — that releases an advisory without one.
2. **No recommendation without a source.** Every recommendation carries the rainfall, pest or plot record it came from. An unsourced recommendation is worse than none.
3. **No real household data.** All records are synthetic. No personally identifying fields exist in the schema: no names, no national ID numbers, no village headman. Households are referenced by an opaque `Household_Ref`.
4. **Never place an order or raise a credit flag.** Out of scope entirely, not gated — simply absent.
5. **The repository must run from a fresh clone.** If a change breaks the quickstart, the change is wrong.

## Stack — locked, do not substitute

- Python 3.11
- LangGraph for orchestration
- Official MCP Python SDK, Streamable HTTP
- Gemma 3 4B (Q4_K_M) via llama.cpp, local, OpenAI-compatible endpoint
- SQLite for records and the pending-approval queue
- JSONL for the audit log
- MIT licence

Do not introduce a new framework, database or model to solve a problem. If one of these is genuinely blocking, say so rather than swapping it out.

## Why these choices

- **LangGraph with explicit nodes and retry edges.** The live technical review adds a new requirement while judges watch. Control flow must be visible and editable on camera, not buried in an agent loop.
- **A 4B model, locally.** 12B does not fit in 8 GB of VRAM and runs at ~3 tok/s with partial offload. 4B runs fully on GPU at ~40 tok/s. The task is constrained extraction and short advisory text — it does not reward parameter count. Local is the privacy claim.
- **SQLite.** One file, no server, keeps the one-command quickstart honest.

## Domain facts

Taken from a structured interview with a field officer. Do not change these without saying why.

- **Effective planting rains:** at least 20–30 mm of continuous moisture over 2–3 days. Confirmed in practice by soil still wet at wrist depth.
- **The failure this exists to prevent:** short showers off the mountain wet the topsoil without creating root-depth moisture. Farmers who plant on them lose hybrid seed and basal fertiliser to the dry spell that follows.
- **Two agroclimatic zones** — lowland and upland — with separate onset thresholds. Blanket advice across zones is a rejection trigger for the approving officer.
- **Delivery is not SMS or USSD.** Advisories are read aloud by lead farmers, broadcast on community radio, or given at village meetings. Write advisory text to be spoken, in plain Chichewa.
- **Feasibility gates recommendations.** Never recommend a seed variety or chemical that is not stocked locally or under AIP.

## Record defects — reproduce, do not clean

The synthetic set deliberately contains four defects characteristic of real paper field registers. Handling them is the point; assuming them away loses the main judging criterion.

- Plot sizes paced or eyeballed rather than measured
- Tenure and plot location stale between seasons (rented plots change)
- Plots recorded as one crop that are really intercropped
- Pest alerts lagging 3–7 days behind first report

Correct behaviour: flag the defect, lower confidence, state it in the advisory. Never silently produce a confident number from a bad record.

## Conventions

- **Log before acting.** Every tool call is appended to the JSONL audit log — inputs, outputs, timestamp — before the agent uses the result.
- **Tools stay small and reusable.** A stranger should be able to call one without the rest of the system. No tool reaches into another's state.
- **Configuration, not code, per district.** Crop calendar and zone thresholds are MCP resources. Supporting another district should mean another resource file.
- **Constrain the model's JSON.** Use schema-constrained decoding rather than parsing hopefully and retrying.
- **Degrade loudly.** On a missing source, fall back and record the substitution. Never invent a figure, never fail silently.

## Writing code here

The live review is twenty minutes: ten walking through this code, then a new requirement added while judges watch. They have said plainly that this is where they separate directing a coding agent from accepting output that cannot be explained.

So:

- Prefer the obvious implementation over the clever one.
- No abstraction that exists only for generality. Three tools that work beat nine that half-work.
- Explain what you wrote and why, in plain terms, as you go.
- If a change is hard to explain in two sentences, it is probably the wrong change.

## Out of scope

Do not build these, even if they seem useful:

- Unattended monitoring or scheduled runs — the officer initiates
- Workflow automation past the approval gate
- Market pricing, credit scoring, traceability — other sub-themes, one project per team
- Any district other than Mulanje
- Cross-session memory. Each advisory run starts clean so runs stay independently auditable.

## Build order

1. Decisions and plumbing ✓
2. Synthetic household set
3. MCP server, `get_rainfall_signal`, `get_household_plots`, audit log
4. `get_pest_alerts`, `check_input_availability`, `draft_advisory`, the approval gate
5. LangGraph orchestration and the recovery path
6. Evals — twelve tasks, five runs each
7. README, ARCHITECTURE.md, EVALS.md, the 300-word description
8. Demo video, submit, stop committing

Borrowed MCP server: **Fetch** (`uvx mcp-server-fetch`) — maintained reference server handling HTTP retrieval, content extraction and robots.txt for published bulletins.

## Keep current

`EVALS.md` gains a case whenever something surprises you during the build — cases found while building are more credible than cases designed in advance.

`README.md` has a "What is unfinished" section. It is meant to be read. Update it; do not quietly delete lines from it.
