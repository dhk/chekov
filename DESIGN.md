# Chekov Design

## 1. Purpose

Chekov is a local-first control plane for agentic work across tools, machines, sessions, and workspaces.

Its primary job is not to record history. Its job is to maintain useful situational awareness:

> What is going on, where is the work headed, what do I want to have happen, and where are those things out of alignment?

This places Chekov between individual agent runtimes and conventional project-management systems.

## 2. Problem

A user may simultaneously have Claude Code running on Linux, Codex running on macOS, ChatGPT conversations contributing research or decisions, multiple worktrees or repositories, investigations that produce no commit, and work represented in Beads or another system.

Existing systems tend to answer only one slice: project management says what has been declared; Git says what changed; agent dashboards say what sessions are running; transcript systems say what an agent executed; retrospective analytics say what happened historically.

Chekov connects current execution to human intent.

## 3. Product model

Chekov maintains four related classes of state.

### Declared intent

An explicit instruction or constraint supplied by the user or imported from a trusted system. Examples include: research whether approach A is viable; do not implement; produce a recommendation; stop after tests pass; compare findings from two agents; wait for review before continuing.

Declared intent should be versioned and attributable.

### Desired state

A condition the user wants to become true. Examples include: a recommendation exists with evidence; a bug has been reproduced; two approaches have been compared; a PR is ready for review; an investigation has reached a decision point.

Desired state describes an outcome or condition rather than an action sequence.

### Observed state

Facts derived from tool integrations and workspace inspection: a session is active, a repository has uncommitted modifications, a session is waiting for input, or an agent is active in a particular workspace.

Observed state must remain separate from interpretations of what that activity means.

### Inferred state

Interpretations derived from observed evidence: the agent appears to be investigating authentication; two sessions may be duplicating work; a session is probably blocked; implementation appears to be occurring despite research-only intent.

Inferred state must retain provenance and confidence.

## 4. Core entities

### Workspace

A durable unit of work. Initial identity signals may include an explicit Chekov workspace ID, Git remote URL, repository root, configured aliases across machines, and filesystem path as a fallback. Absolute paths alone are insufficient because the same workspace may live at different paths on different machines.

### Host

A machine participating in Chekov, with a stable host ID, human-readable hostname, operating system, and last-seen timestamp.

### Agent runtime

A tool family such as Claude Code, Codex, ChatGPT, or a future CLI/desktop agent.

### Session

A runtime-specific execution context with a normalized session ID, runtime, host, workspace, start time, last activity, lifecycle state, and source reference.

### Intent

A user-authored statement of purpose, constraint, or requested direction. Intent may apply to a workspace, investigation, or individual session.

### Desired state

A user-authored outcome or stopping condition.

### Observation

A deterministic or source-derived fact.

### Inference

A semantic interpretation of one or more observations.

### Exception

A mismatch worth surfacing between intent, desired state, observed state, or inferred state.

## 5. High-level architecture

```text
Claude Code ---------+
Codex ---------------+
ChatGPT -------------+
Other runtimes ------+
                     |
                     v
               Runtime adapters
                     |
                     v
            Normalized observations
                     |
                     v
             Local Chekov store
              /       |       \
             /        |        \
        Intent    Desired state  Workspace state
             \        |        /
              \       |       /
               Reconciliation
                     |
                     v
             CLI / API / MCP
```

The first implementation should not require a central hosted service.

## 6. Collection strategy

Adapters should prefer existing runtime state over invasive instrumentation. Potential sources include runtime-maintained session stores, lifecycle hooks, process inspection, workspace filesystem state, Git status, and explicit Chekov commands.

Collection should normalize source-specific events without erasing source provenance. Chekov should not require every runtime to expose identical fidelity.

A normalized observation may be as small as:

```json
{
  "timestamp": "2026-08-26T17:12:31-07:00",
  "host_id": "lobster",
  "runtime": "claude-code",
  "session_id": "abc123",
  "workspace_id": "identity-matching",
  "type": "session.activity",
  "source": "claude-session-store"
}
```

Semantic meaning belongs in a separate inferred record.

## 7. Intent capture

Intent must be cheap to declare. Initial interfaces should support something like:

```bash
chekov want "Determine whether clinical evidence improves identity matching"
chekov constrain "Research only; do not implement"
chekov next "Reconcile the Claude and Codex findings"
```

Intent capture should not require creating Jira-style issue structures.

Intent can later be imported from Beads or other work systems, but imported state must preserve source and authority.

## 8. Reconciliation

The reconciliation engine should begin with deterministic rules.

Examples:

- **No active owner:** desired state is unresolved and no relevant session has recent activity.
- **Research-only violation:** declared constraint says research-only while observed workspace state shows implementation-oriented changes.
- **Duplicate activity:** two active sessions are associated with the same workspace and appear to touch the same objective.
- **Waiting for attention:** a session is in a waiting/needs-input state beyond a configurable threshold.
- **Goal reached but work continues:** a desired state is explicitly marked satisfied while related sessions remain active.

Semantic reconciliation can later use model-assisted interpretation, but deterministic rules should remain independently visible.

## 9. Beads integration

Beads is an integration, not Chekov's database.

Beads may supply declared work, dependencies, durable agent memory, statuses, and discovered work. Chekov adds current runtime activity, cross-machine/session presence, user-level desired state, and reconciliation between declared work and observed execution.

Useful discrepancies include active work with no corresponding Bead, a Bead in progress with no active/recent agent, multiple agents apparently acting on one Bead, or observed activity that conflicts with Bead constraints or user intent.

Chekov should remain useful without Beads installed.

## 10. Relationship to Work-Ledger

Chekov and Work-Ledger solve different temporal questions.

**Work-Ledger:** What happened?

**Chekov:** What's going on, where is it headed, and what do I want to happen next?

Future integration may be valuable, but neither system should be reduced to the other.

## 11. Storage

The MVP should use a local durable store, likely SQLite. The schema should distinguish immutable/source observations, user-declared intent, desired states, inferred semantic state, exceptions, and runtime/source cursors.

Raw runtime transcripts do not need to be duplicated if source references are durable and readable.

## 12. Cross-machine model

The MVP should first make a single machine useful. Cross-machine support should preserve the same model: each machine has a stable host ID, each host collects locally, observations can synchronize to a user-controlled coordinator, temporary network loss does not block local operation, and synchronization avoids raw transcript content unless explicitly configured.

## 13. CLI target

```text
$ chekov

4 workspaces · 7 agents · 2 machines

IDENTITY-MATCHING
Wanted: Determine whether clinical evidence improves matching

  claude@lobster   investigating DOB drift       active
  codex@mac        testing scoring thresholds    active

  ON COURSE
  Next: reconcile findings

TRICORDER
Wanted: Complete PR maturity analysis

  claude@mac       waiting for input             37m

  NEEDS ATTENTION
  No active session owns the unresolved review

EXCEPTIONS
  Codex appears to be implementing in a research-only workspace
  Two active sessions may be duplicating the same investigation
```

The CLI should privilege actionable exceptions over exhaustive telemetry.

## 14. MCP/API

A read-oriented MCP surface is useful early because it lets an agent understand the wider work environment. Candidate operations include `chekov.status()`, `chekov.workspace(id)`, `chekov.active()`, `chekov.intent(workspace)`, `chekov.exceptions()`, and `chekov.want(...)`.

Mutation and agent-control operations should come later and follow the Constitution's explicit-control principle.

## 15. Privacy and security

The system should default to local storage, collect the minimum needed to establish useful state, avoid copying raw transcript bodies unless required, make network paths explicit, allow workspace-level exclusion, avoid exposing secrets from command arguments or environment variables, and preserve source provenance without unnecessarily duplicating sensitive content.

## 16. Non-goals for the MVP

Chekov is not initially a Jira or Linear replacement, a Beads replacement, a transcript archive, a general LLM observability platform, a team productivity scorecard, a hosted multi-tenant service, an agent orchestrator, a workflow engine, an autonomous manager of agents, or a web dashboard.

## 17. MVP acceptance criteria

A useful first vertical slice should allow one user on one machine to:

1. discover active/recent Claude Code and Codex sessions;
2. associate them with durable workspace identities;
3. see whether sessions are active, idle, or waiting;
4. declare a desired outcome for a workspace;
5. declare at least one constraint;
6. inspect uncommitted workspace state where Git is present;
7. see a compact `chekov` status view;
8. receive at least two deterministic exception types;
9. trace every displayed assertion to either user intent or source evidence;
10. operate without a hosted service.

Once this works well, cross-machine aggregation is the next forcing function.
