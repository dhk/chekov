# Chekov Roadmap

This roadmap describes intended sequencing, not promises. Items move forward when the preceding layer proves useful.

## Product objective

Create a control plane for agentic work that lets a user understand:

- what is going on now;
- what they want to have happen;
- whether current activity is moving toward that state;
- where their attention or course correction is needed.

## Phase 0 — Product definition

**Status: complete except the prior-art review**

Establish the product boundary and vocabulary.

Delivered:

- Constitution;
- design document;
- roadmap;
- repository README;
- explicit separation from Work-Ledger;
- explicit integration boundary with Beads and task systems.

Planned, not yet done:

- initial prior-art review (no review document exists in this repository yet).

Exit criteria:

- the product can be explained without describing it as a task tracker, transcript viewer, or retrospective analytics tool;
- current state, intent, desired state, and exceptions are independently defined.

## Phase 1 — Single-machine situational awareness

**Status: implemented**

**Goal:** Answer “what's going on?” reliably on one machine.

Build:

- Python package and `chekov` CLI;
- local SQLite state;
- host identity;
- workspace discovery and identity;
- Claude Code session adapter;
- Codex session adapter;
- active/recent/idle/waiting session state;
- Git working-tree observation when present;
- source provenance;
- basic status output.

Target:

```text
$ chekov

3 workspaces · 5 recent sessions

CHEKOV
  codex       active      implementing session adapter
  claude      14m         reviewing schema

WORK-LEDGER
  claude      waiting     needs input

UNCOMMITTED
  chekov      6 files
```

Exit criteria:

- Chekov accurately identifies the relevant active/recent sessions for the user's normal Claude Code and Codex workflow;
- absolute filesystem paths are not the only workspace identity;
- status is useful without LLM interpretation.

## Phase 2 — Intent and desired state

**Goal:** Answer “what do I want to have happen?”

Build lightweight declaration surfaces for desired outcome, current objective, constraints, next wanted state, and pause/stop conditions.

Possible CLI:

```bash
chekov want "Produce a recommendation on storage architecture"
chekov constrain "Research only; do not implement"
chekov next "Compare Claude and Codex findings"
```

Build versioned intent records, scope them to workspaces and optionally sessions/investigations, preserve the distinction between explicit and imported intent, and render desired state next to observed activity.

Exit criteria:

- declaring direction is materially cheaper than creating a conventional ticket;
- status can answer both “what's happening?” and “what do I want?”

## Phase 3 — Deterministic reconciliation

**Goal:** Surface useful mismatches without requiring an LLM.

Initial exception rules:

- desired outcome has no recent active session;
- session is waiting for input;
- multiple active sessions in the same workspace;
- research-only constraint with implementation-oriented workspace changes;
- desired state marked complete while related work remains active;
- active work exists with no declared intent.

Build an exception lifecycle, severity/attention model, suppression/acknowledgement, and provenance explaining why each exception fired.

Exit criteria:

- the top-level status view highlights exceptions that regularly cause the user to redirect work;
- false-positive burden is low enough that the user does not learn to ignore the view.

## Phase 4 — Cross-machine aggregation

**Goal:** Make Chekov useful across macOS and Linux simultaneously.

Build:

- stable host registration;
- local event/observation queue;
- user-controlled coordinator;
- sync protocol;
- conflict-resistant IDs;
- offline operation;
- machine aliases;
- workspace aliasing across hosts.

Security requirements:

- no mandatory transcript-body synchronization;
- explicit network configuration;
- authenticated host enrollment;
- clear visibility into what is synchronized.

Exit criteria:

- one `chekov` view accurately shows current/recent work across the user's primary machines.

## Phase 5 — Beads integration

**Goal:** Reconcile declared durable work with observed agent activity.

Read first: Beads/issues, dependencies, status, and durable memory where appropriate.

Surface discrepancies such as active work with no Bead, a Bead in progress with no recent work, multiple agents acting on one Bead, user intent conflicting with Bead state, or work apparently completed but durable state not updated.

Only after read/reconciliation proves useful should Chekov consider writing state back to Beads.

Exit criteria:

- Beads becomes richer because Chekov can show where declared work and actual execution differ;
- Chekov remains useful when Beads is absent.

## Phase 6 — Semantic work state

**Goal:** Understand what agents are working on, not merely that they are active.

Add inferred concepts such as investigation, implementation, review, experiment, question, finding, and decision point.

Principles:

- deterministic evidence remains visible;
- inferred state is labeled;
- every inference retains provenance and confidence;
- inference does not silently modify user intent.

Potential capabilities include duplicate investigation detection, recognizing when one agent is blocked on something another resolved, detecting convergent independent findings, and surfacing semantic divergence from desired outcomes.

Exit criteria:

- semantic inference produces useful course-correction signals beyond what deterministic rules can provide.

## Phase 7 — Agent-facing situational awareness

**Goal:** Let agents benefit from the wider operational picture.

MCP/read APIs can answer:

- what other agents are working in this workspace?
- what does the user currently want?
- what constraints apply?
- what unresolved exceptions exist?
- has another agent already investigated this?

Chekov should initially provide context, not autonomous coordination.

Exit criteria:

- agents duplicate less work and respect declared constraints more reliably when Chekov context is available.

## Phase 8 — Explicit control

**Goal:** Allow deliberate course correction from one control surface.

Candidates include pausing/resuming sessions where runtime APIs permit, sending updated intent, requesting handoff, marking desired state satisfied, assigning a next investigation, or telling an agent to stop at a boundary condition.

This phase must preserve the constitutional rule:

> Chekov is the navigator, not the captain.

Any control action must be attributable to the user or an explicit user-authored policy.

## Later / deliberately uncommitted

These ideas require evidence before entering the active roadmap:

- web dashboard;
- mobile status;
- team/multi-user operation;
- hosted synchronization;
- Jira/Linear write-back;
- automatic agent scheduling;
- automatic spawning of new agents;
- policy-driven autonomous coordination;
- historical integration with Work-Ledger;
- fleet-level optimization.

## Success measures

Early product success should be qualitative and operational, not productivity scoring.

Useful questions include:

- Did Chekov tell the user something important they did not already know?
- Did it reveal work moving in the wrong direction?
- Did it prevent duplicated investigation?
- Did it reveal unattended or blocked work?
- Could the user reconstruct the current operational picture faster than by visiting each agent?
- Did declared intent reduce the need to repeatedly reorient agents?

The product should earn complexity only by improving those outcomes.
