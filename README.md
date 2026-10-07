# Mvula

An agentic advisory assistant for the Mulanje District Extension Office, Malawi.

**Challenge:** African Agentic AI Design Challenge — Agriculture track ("The Extension Backlog")
**Sub-theme:** Climate-smart advisory
**Status:** In development. See [What is unfinished](#what-is-unfinished) 

> *Mvula* is Chichewa for rain. Working name, not final.

---

## What this does

An Extension Planning Area field officer in Mulanje is responsible for roughly 1,500–2,500 farming households and reaches 600–800 of them directly in a season. Rainfall bulletins, pest reports and household plot records have to be cross-checked by hand before any advice goes out, and a forecast takes 5–10 days to travel from the meteorological service to a conversation in a village.

Mvula drafts a section-level planting and spraying advisory from those signals, cites the record behind every recommendation, and stops. A named officer approves before anything reaches a household.

The agent never sends advice, never places an input order, and never raises a credit flag.

## The decision it models

Mulanje's characteristic failure is the false start. Short showers off the mountain wet the topsoil without creating root-depth moisture; farmers who plant on them lose hybrid seed and basal fertiliser to the dry spell that follows, and replant at their own cost.

The agent's core rule, taken from field practice: effective planting rains mean **at least 20–30 mm of continuous moisture over 2–3 days**, confirmed by soil that stays wet at wrist depth.

Its most useful output is therefore often *hold*, with the rainfall record that justifies holding.

## Who it is built for

Built around the workflow of a field officer at the Mulanje District Agricultural Office, based on a structured interview conducted during the build period. Design decisions traceable to that interview are marked in [ARCHITECTURE.md](ARCHITECTURE.md).

Advisories are drafted for delivery by lead farmer, community radio and village meeting — not SMS or USSD. Phone ownership, network coverage and airtime make push messaging unreliable in the target area.

## Quickstart

```
# not yet implemented — a single command will go here, and it will be tested from a fresh clone
```

Requires Python 3.11+ and a local [Gemma](https://ai.google.dev/gemma) instance.

## Architecture

A LangGraph agent over a purpose-built MCP server, plus one borrowed MCP server.

| Tool | Does |
|---|---|
| `get_rainfall_signal` | Gauge and satellite rainfall, evaluated against the effective-onset rule |
| `get_household_plots` | Plot and planting records, returned with data-quality flags |
| `get_pest_alerts` | District pest alerts, with reporting lag stated |
| `check_input_availability` | Whether recommended seed or inputs can actually be sourced locally |
| `draft_advisory` | Composes a sourced advisory and queues it for officer approval |

Every tool call is logged to JSONL with inputs, outputs and timestamp. `draft_advisory` is gated: it cannot complete without a named approver recorded.

Full detail in [ARCHITECTURE.md](ARCHITECTURE.md).

## Data

**All household and plot data in this repository is synthetic.** No real household's records are used.

The record schema mirrors a real Extension Planning Area field register, with all personally identifying fields removed — household and household-head names, national ID numbers and village headman names are not present. Households are referenced by an opaque `Household_Ref`.

The synthetic set deliberately reproduces four defects that are characteristic of real field registers:

- Plot sizes estimated by eye or pacing rather than measured
- Tenure and plot location records that have gone stale between seasons
- Plots recorded as a single crop that are in practice intercropped
- Pest alerts arriving 3–7 days behind first report

These are not cleaned up. Handling them — flagging a stale record, lowering confidence, saying so in the advisory — is part of what the agent is for.

Rainfall and pest data sources, and what they do not cover, are documented in [ARCHITECTURE.md](ARCHITECTURE.md).

## Evaluation

See [EVALS.md](EVALS.md) for the test set, pass and fail results, run-to-run variation, and one failure left unfixed.

## What is unfinished

*Updated as the build proceeds. This section is meant to be read.*

- Everything below Day 1 of the build plan
- No quickstart command yet
- No evaluation results yet
- Advisory text has not been reviewed by a Chichewa speaker working in extension
- Single district, two agroclimatic zones; nothing here is validated outside Mulanje

## Licence

MIT. See [LICENSE](LICENSE).

Gemma is used under Google's own model terms, which are separate from this repository's licence.
