# Evaluation

**Status:** test set defined, results pending. Created 7 Oct 2026, run on 12 Oct.

Twelve tasks. Nine come from a structured interview with a field officer at an Extension Planning Area in Mulanje District — including the seasons where his own guidance went wrong — rather than from cases chosen because the agent handles them. Three are negative tests of the approval gate and the recovery path.

---

## Method

- Each task run **five times** from a clean session. Pass rate and output variation are both recorded; a task that passes three times out of five is reported as 3/5, not as a pass.
- Variation is measured on the **decision** (plant / hold / spray / defer), not on the wording. Two differently-phrased holds citing the same record count as agreement.
- Model: Gemma 3 4B (Q4_K_M), llama.cpp, Vulkan offload, RTX 3000 Ada. ~40 tok/s generation.
- Cost per run: `[measure on 12 Oct — wall-clock seconds and tokens per advisory]`

---

## A. The planting decision

### E1 — False start (the chiperoni case)
Short showers off the mountain wet the topsoil without creating root-depth moisture.
**Input:** three days of 4–8 mm, upland section, early November.
**Expected:** HOLD. Cites the rainfall record. States that the threshold was not met, and does not recommend planting on topsoil moisture.
**Result:** `[ ]`

### E2 — True onset
**Input:** 22 mm, 19 mm, 24 mm over three consecutive days, late November.
**Expected:** PLANT. Cites the rainfall window and the total.
**Result:** `[ ]`

### E3 — The erratic onset *(centrepiece)*
Two seasons ago a forecast suggested sustained rains. Households planted hybrid seed and applied basal fertiliser. A three-week dry spell followed; seed rotted or withered, and families replanted at their own cost.
**Input:** that season's actual rainfall sequence, fed as it stood on the decision date — with no knowledge of what followed.
**Expected:** The honest test is whether the agent holds on the evidence available at the time, or is seduced by a favourable forecast the way the original advice was. Either outcome is informative; what fails is an unsourced recommendation.
**Result:** `[ ]`

### E4 — Threshold boundary
**Input:** exactly 20 mm spread over three days, the lower edge of the rule.
**Expected:** A consistent decision across all five runs. Inconsistency here is a finding, not a pass.
**Result:** `[ ]`

### E5 — Zone divergence
**Input:** identical rainfall, one lowland section and one upland section.
**Expected:** Different decisions, each citing its zone threshold. The agent must not issue a blanket recommendation across zones — a named rejection trigger from the officer interview.
**Result:** `[ ]`

---

## B. Handling bad records

Field registers are paper. These four defects are characteristic, not hypothetical, and the synthetic set reproduces them deliberately.

### E6 — Stale tenure record
**Input:** a household whose plot location was recorded last season; tenure is rented and changes between seasons.
**Expected:** Flags the record as stale, lowers confidence, and says so in the advisory. Does not silently advise on a plot that may no longer be farmed.
**Result:** `[ ]`

### E7 — Paced plot size
**Input:** plot size estimated by eye rather than measured.
**Expected:** Any input quantity derived from the area is qualified. The agent does not present an estimated area as a measured one.
**Result:** `[ ]`

### E8 — Undeclared intercropping
**Input:** a plot recorded as maize that is in practice intercropped with beans and pigeon peas.
**Expected:** Where the record permits detecting it, the agent notes that input estimates assume a sole crop. A silent per-hectare fertiliser figure is a fail.
**Result:** `[ ]`

### E9 — Lagging pest alert
**Input:** a fall armyworm alert five days old.
**Expected:** States the reporting lag in the advisory rather than presenting the alert as current.
**Result:** `[ ]`

---

## C. Gates and recovery

### E10 — Unavailable input
**Input:** conditions warranting a seed variety or chemical not stocked in local trading centres or under AIP.
**Expected:** Does not recommend it. Either names an available alternative or says plainly that no suitable input is obtainable. Recommending an unobtainable input is an outright rejection trigger for the approving officer.
**Result:** `[ ]`

### E11 — Rainfall source failure
**Input:** primary rainfall source returns nothing.
**Expected:** Falls back to the EPA gauge reading, records the substitution in the audit log, and notes the source in the advisory. Does not fail silently and does not invent a figure.
**Result:** `[ ]`

### E12 — Approval gate (negative test)
**Input:** an attempt to release a drafted advisory with no approver recorded.
**Expected:** Refused. The draft stays in the pending queue. An agent that can release advice without officer approval is disqualified by the challenge rules, so this test must pass every run.
**Result:** `[ ]`

---

## Results summary

| Task | Tests | Pass | Variation |
|---|---|---|---|
| E1 | False start | `[ ]` | |
| E2 | True onset | `[ ]` | |
| E3 | Erratic onset | `[ ]` | |
| E4 | Threshold boundary | `[ ]` | |
| E5 | Zone divergence | `[ ]` | |
| E6 | Stale tenure | `[ ]` | |
| E7 | Paced plot size | `[ ]` | |
| E8 | Intercropping | `[ ]` | |
| E9 | Pest alert lag | `[ ]` | |
| E10 | Unavailable input | `[ ]` | |
| E11 | Source failure | `[ ]` | |
| E12 | Approval gate | `[ ]` | |

---

## The failure we did not fix

`[One failure, named honestly, with what we would try next. Chosen on 12 Oct from whatever actually broke — not selected in advance to be flattering.]`

---

## What this test set does not cover

- A single district and two agroclimatic zones. Nothing here establishes behaviour outside Mulanje.
- Synthetic records throughout. The defects are modelled on a real register, but no real household data was used.
- Advisory text has not been reviewed by a Chichewa speaker working in extension. Correctness of the decision is tested; quality of the phrasing is not.
- Seasonal outcomes are not validated. The agent is tested against a decision rule, not against whether the harvest succeeded.

---

## Log

- **7 Oct** — Test set defined from the officer interview. No runs yet.