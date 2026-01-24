# skills/skill-creator

本目录存放内置技能 **skill-creator** 的 canonical 定义。

## 包含内容

- **skillspec.json**：该技能的规格定义。
- **references/**：skill 系统设计、工作流模式、交付检查清单等说明文档。
- **scripts/**：占位/示例脚本（如果需要可替换为实际确定性工具）。

## 约定

- `skillspec.json` 变更后应通过 `skill-creator generate` 重新生成各 target 输出并校验。
