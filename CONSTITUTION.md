# Chekov Product Constitution

This document defines the durable principles that govern Chekov. Implementation choices, integrations, and roadmap items may change; these principles should change rarely and deliberately.

## 1. The user is the captain

Chekov is a navigator, not a captain.

The user's intent, constraints, and desired outcomes are authoritative. Chekov may surface contradictions, missing information, risks, or more efficient courses, but it must not silently replace the user's goals with its own.

## 2. Present state and desired state are both first-class

Chekov exists to reconcile:

- **observed state** — what agents and workspaces appear to be doing now;
- **declared intent** — what the user has asked to happen;
- **desired state** — what the user wants to become true.

A system that only observes agents is a dashboard. A system that only stores desired work is a task manager. Chekov must preserve both sides and make their relationship visible.

## 3. Work is broader than tickets and commits

Investigations, experiments, comparisons, reviews, decisions, questions, and abandoned approaches are work even when they produce no Git commit and no Jira ticket.

Chekov must not define work solely through repository history or project-management artifacts.

## 4. Observation is not intention

Evidence that an agent opened files, ran commands, edited code, or spent time in a workspace does not prove why it did so.

Chekov must distinguish observed facts from inferred meaning and from explicitly declared intent.

## 5. Inference must remain visibly inference

Chekov may infer likely investigations, duplicated effort, stalled work, or course divergence. Machine inference must never be silently promoted to user intent or authoritative state.

Every inferred state should preserve enough provenance for a user to understand why Chekov believes it.

## 6. Exceptions are a primary product surface

The most useful information is often disagreement:

- an agent is implementing when the user asked for research only;
- two agents appear to be doing the same work;
- a desired outcome has no active owner;
- a session is blocked on a question another agent has already answered;
- work continues after the requested stopping condition;
- an active session has no identifiable objective.

Chekov should prioritize these mismatches over exhaustive telemetry.

## 7. Local-first by default

Core state collection, reconciliation, and inspection should work locally without requiring a hosted service.

Networked synchronization may be added, but the product must make network boundaries explicit and preserve meaningful local functionality when disconnected.

## 8. Cross-tool and cross-machine are core, not edge cases

Chekov exists because agentic work is fragmented across runtimes, machines, and interaction surfaces.

No individual agent vendor, operating system, repository host, or task system may become the definition of the product model.

## 9. Integrate rather than replace

Chekov should interoperate with systems that already represent durable work or memory, including Beads, GitHub, Jira, Linear, and future systems.

Those systems may be sources or destinations of declared state. Chekov should not recreate a task tracker merely to own the data.

## 10. Provenance matters

Important assertions should be traceable to their source: user declaration, agent session, workspace state, external system, or inference.

Summaries are useful; recoverable evidence is essential.

## 11. Privacy is a product requirement

Agent sessions may contain source code, secrets, personal data, customer data, or confidential reasoning.

Chekov must minimize collection, make retention explicit, avoid unnecessary duplication, and never silently transmit session content to hosted models or services.

## 12. No productivity surveillance

Chekov is for situational awareness and direction, not worker scoring.

Metrics such as time active, tokens used, commands run, or files touched must not be treated as proxies for individual productivity or performance.

## 13. Deterministic evidence before model interpretation

Where reliable state can be derived from deterministic sources — process state, timestamps, repository status, session metadata, declared configuration — Chekov should use those before invoking language-model interpretation.

LLM interpretation should enrich evidence, not substitute for evidence that can be obtained directly.

## 14. Course correction should be explicit

Chekov may eventually help redirect, pause, resume, or coordinate agents. Any action that changes agent execution must be attributable to an explicit user policy or command.

Observation and control must remain separable.

## 15. Chekov should reduce cognitive load, not create another inbox

The product succeeds when a user can quickly understand:

- what matters now;
- what is on course;
- what needs attention;
- what is waiting;
- what should happen next.

More events, alerts, and dashboards are not inherently better.
