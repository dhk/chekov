# Chekov

**A control plane for agentic work: see what your agents are doing, where the work is headed, and what you want to happen next.**

Chekov provides situational awareness across AI-assisted work spread across tools, machines, sessions, and workspaces.

It is built around three questions:

1. **What's going on?** — What are agents doing now, what are they waiting on, and what work appears active?
2. **What do I want to have happen?** — What outcomes, constraints, and next states has the user declared?
3. **Are those aligned?** — Where is observed activity diverging from intent, duplicating effort, stalling, or proceeding without sufficient direction?

Chekov is not a Jira replacement, not an agent transcript archive, and not primarily a retrospective analytics tool. It lives beneath conventional project management and above individual agent runtimes.

```text
Declared intent        Observed activity        Desired state
      \                       |                      /
       \                      |                     /
        +------------------- Chekov ----------------+
                            |
                            v
                 Situational awareness
                            |
                            v
              Attention / course corrections
```

## Product boundary

Chekov is deliberately present- and future-oriented.

- **Work-Ledger** asks: *What happened?*
- **Chekov** asks: *What's going on, where is it headed, and what do I want to happen next?*
- **Beads and similar systems** may represent declared work, dependencies, and durable agent memory. Chekov can integrate with them, but does not replace them.

The disagreement between declared intent and observed activity is often the most valuable signal in the system.

## Core concepts

### Workspace

A durable identity for a body of work. A workspace may appear at different filesystem paths on different machines and may contain multiple repositories or no repository at all.

### Agent session

A bounded execution context from Claude Code, Codex, ChatGPT, another CLI agent, or a future integration.

### Intent

What the user has asked an agent, workspace, or investigation to accomplish. Intent may include constraints such as *research only*, *do not implement*, *stop after producing a recommendation*, or *do not touch production*.

### Desired state

A condition the user wants to become true. Desired state is not necessarily a task list. It may be an outcome, decision point, artifact, level of confidence, or stopping condition.

### Observed state

What Chekov can determine is actually happening from agent/session telemetry and workspace evidence.

### Exception

A meaningful mismatch between observed state, declared intent, and desired state. Examples include duplicated investigations, implementation occurring during a research-only phase, work continuing after the desired state has been reached, or important desired outcomes with no active agent.

## First target experience

```text
$ chekov

4 workspaces · 7 agents · 2 machines

IDENTITY-MATCHING
Desired: Determine whether clinical evidence improves matching

  claude@lobster   investigating DOB drift       active
  codex@mac        testing scoring thresholds    active

  ON COURSE
  Next: reconcile findings and produce recommendation

TRICORDER
Desired: Complete PR maturity analysis

  claude@mac       waiting for input             37m

  NEEDS ATTENTION
  No agent currently owns the unresolved review step

EXCEPTIONS
  Codex is modifying implementation in a research-only workspace
  Two agents appear to be investigating the same question
```

## Governance

The repository's product hierarchy is:

**[CONSTITUTION.md](CONSTITUTION.md) → [DESIGN.md](DESIGN.md) → [ROADMAP.md](ROADMAP.md) → implementation**

The Constitution contains enduring product constraints. The Design describes the initial system model. The Roadmap orders delivery without turning speculative capabilities into commitments.

## Status

Chekov is at product-definition stage. The first implementation milestone is a local-first CLI that can identify active/recent Claude Code and Codex sessions across a machine, associate them with workspaces, attach declared intent, and surface useful mismatches.
