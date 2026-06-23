# Neo Skills

我常用的 Codex skills。

## 技能清单

| 技能 | 说明 |
| --- | --- |
| `neo-task-governance` | 解决超大型任务中 Agent 上下文丢失、执行不连续、重复犯错的问题，把任务推进拆成有边界、有记录、有验证的流程。 |
| `neo-cpp-refactor` | 固化较好的 C++ 实践要求，用于代码重构时统一命名、注释、边界、安全性和验证标准。 |
| `neo-mail-assistant` | 弥补个人沟通中不够谨慎、容易留下漏洞的问题，用邮件材料辅助措辞、归纳证据和判断协作边界。 |
| [taste-skill](https://github.com/leonxlnx/taste-skill) | 个人优选开源 skill，面向 UI 设计新手也足够友好，帮助开发者快速获得一套均衡、耐看、少 AI 味的 UI/UX 设计判断。 |

## 安装方式

通过 npx 安装到当前用户的 Codex skills 目录：

```bash
npx @neo_lmx/neo-skill install
```

查看包内技能：

```bash
npx @neo_lmx/neo-skill list
```

安装到自定义目录：

```bash
npx @neo_lmx/neo-skill install --target <path>
```

复制单个 skill 到 Codex skills 目录：

```powershell
Copy-Item -Recurse .\skills\neo-task-governance $env:USERPROFILE\.codex\skills\
```

或一次性同步全部公开 skills：

```powershell
.\tools\sync-to-codex-skills.ps1
```

安装后，可以在对话中按名称触发：

```text
$neo-task-governance 帮我治理这个迁移任务
$neo-cpp-refactor 重构这些 C++ 文件
$neo-mail-assistant 把这些邮件材料整理成任务记录
```

## 维护

发布前运行校验：

```powershell
.\tools\validate-skills.ps1
```
