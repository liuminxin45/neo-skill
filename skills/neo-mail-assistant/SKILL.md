---
name: neo-mail-assistant
description: "基于邮件材料进行任务整理、沟通拟稿、证据归纳、工作记录生成和协作边界判断。"
---

# Mail Assistant

## Activation

Use this skill when the user asks to reason, draft, review, summarize, or plan
from email-like work material, including sent mail, meeting notes, issue
threads, follow-up records, status reports, and task evidence.

## Method

This skill uses the following support files:

- `work.md` contains reusable workflows, decision standards, output preferences, and evidence-handling rules.
- `persona.md` contains generic communication style guidance and collaboration boundaries.
- `evidence.jsonl` contains evidence index records.
- `evidence_digest.md` contains aggregated evidence themes and usage notes.
- `sources.json` records generation metadata.

## Use Rules

- Prefer `work.md` for task execution, structured summaries, and technical judgment.
- Use `persona.md` only for tone, collaboration expectations, and boundary interpretation.
- Cite repository evidence with neutral labels such as `[E001]` only for generic working patterns.
- Cite user-provided material separately with labels such as `[U1]`, `[U2]` when concrete current-context evidence is needed.
- Do not fabricate promises, approvals, senders, recipients, deadlines, or decisions.
- If evidence is insufficient, say `资料不足`.
- Do not fabricate private details or infer information that is not present in the provided material.

## Artifacts

- work.md
- persona.md
- evidence.jsonl
- evidence_digest.md
- sources.json

## Status

- raw_evidence: excluded
- evidence_index: included
