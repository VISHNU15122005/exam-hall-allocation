# AI Prompts

## Feature Request — Recorded in Source Report

> Modify the Exam Hall Allocation System so that students from the same class/section should not be seated next to each other whenever possible. Requirements: every valid student gets exactly one seat; no seat assigned twice; hall capacity never exceeded; multiple halls continue working; existing validation continues working; no regression.

## Design Guidance Preserved by the AI Record

- Adjacency = same hall + same row + column difference 1.
- Preserve existing register-number order.
- Prefer a free seat without a same-Class/Section neighbor.
- Fall back to the first free seat if no preferred seat exists.
- Preserve the higher-priority requirement to seat everyone.

## Deliberate RED Prompt / Action

The capacity comparison was intentionally weakened from `>=` to `>` to create a controlled failure and demonstrate the RED → diagnosis → restoration → GREEN loop.

## Scope Note

This file includes the prompts/actions explicitly preserved in the audit report. It does not claim to reproduce a complete hidden Claude transcript.
