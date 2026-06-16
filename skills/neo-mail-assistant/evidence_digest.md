# Evidence Digest

This digest summarizes evidence patterns extracted from email-like work
materials.

## Evidence Themes

| Evidence | Theme | Reusable Pattern |
| --- | --- | --- |
| E001 | Testing governance | Use tables to align product line, test type, expected timing, dependency, and owner role. |
| E002 | Project status | Report by module, owner role, current progress, next plan, overall progress, and target time. |
| E003 | Issue triage | Separate symptom, reproduction, logs/data, affected scope, and responsibility boundary. |
| E004 | Cross-team coordination | Convert meeting conclusions into roles, actions, deadlines, and verification tasks. |
| E005 | Technical topic tracking | Track topic name, milestone, risk, current state, and next step. |
| E006 | Quality process | Explain process gaps with timeline, executed actions, uncovered cases, and closure plan. |
| E007 | Data security | Prioritize by sensitivity and severity, then land changes in staged batches. |
| E008 | Technical assessment | Compare feasibility, resource cost, maintenance cost, risk, and alternatives. |
| E009 | Knowledge management | Maintain technical notes by topic tree, link, owner role, and update cadence. |
| E010 | Onboarding and task split | Break work into staged commits, business familiarization, issue fixing, and review feedback. |
| E011 | Data analysis | Group by version, environment, error type, or scenario before drawing conclusions. |
| E012 | Boundary and risk | Mark evidence gaps, escalation points, and decisions that require human confirmation. |

## Usage Notes

- Use evidence IDs only for generic method support, for example `[E003]`.
- Do not present these records as raw factual proof for a specific current task.
- For user-provided current materials, create separate temporary labels such as `[U1]`.
- If current material conflicts with repository evidence patterns, current material wins.
- If evidence is insufficient, output `资料不足`.
