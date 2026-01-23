# Requirement Collection Protocol

Guide for collecting skill requirements through conversational Q&A (max 10 questions).

## Priority Order

Ask questions in this priority order (skip if already known):

1. **Goal** - What is the one-sentence objective? (verb-based, repeatable task)
2. **Triggers** - What phrases/keywords will users say? (at least 5)
3. **Output** - What form should the output take? (code/report/checklist/patch)
4. **Constraints** - What are the hard limits? (no network/must test/read-only)
5. **Tools** - What tools are allowed? (shell/git/python/file ops)
6. **Inputs** - What inputs are needed? (repo/config/logs/diff)
7. **Workflow** - What are the key steps? Where are the gates?
8. **Edge Cases** - What failures are expected? How to handle?
9. **Resources** - What goes to references/scripts/assets/.shared?

## Question Templates

### Goal Question
```
这个 skill 的一句话目标是什么（动词开头，面向可重复任务）？
What is the one-sentence goal of this skill (verb-based, for repeatable tasks)?
```

### Trigger Question
```
用户会用哪些触发语句/关键词来表述这个需求（至少 5 条）？
What trigger phrases/keywords will users say? (at least 5 examples)
```

### Output Question
```
期望输出是什么形态？
- 报告 (report/analysis)
- 代码 (code generation)
- 补丁 (patch/diff)
- 命令 (shell commands)
- 文件树 (directory structure)
- 清单 (checklist)
- 其他
```

## Inference Rules

Before asking, try to infer from context:

| If user says... | Infer... |
|-----------------|----------|
| "review", "audit", "check" | Output = checklist, Workflow = gated |
| "generate", "create", "build" | Output = code/files, Freedom = low-medium |
| "fix", "debug", "repair" | Output = patch, Tools = git/diff |
| "explain", "document" | Output = report, Freedom = high |
| "convert", "migrate" | Output = transformed code, Tools = file ops |

## Stop Conditions

Stop collecting when:
- All 9 priority items are known
- 10 questions reached
- User explicitly says "够了" / "that's enough"

## Output Format

After collection, summarize in this format:

```markdown
## Skill Requirements Summary

- **Goal**: [one sentence]
- **Triggers**: [list of 5+]
- **Output**: [form]
- **Constraints**: [hard limits]
- **Tools**: [allowed tools]
- **Inputs**: [required inputs]
- **Workflow**: [key steps]
- **Edge Cases**: [failure handling]
- **Resources**: [distribution plan]
```
