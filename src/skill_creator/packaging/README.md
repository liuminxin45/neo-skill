# src/skill_creator/packaging

本目录存放技能打包相关逻辑。

## 职责

- 将生成的 Claude 目标目录打包为 `.skill`（zip），并确保根目录结构符合 Claude 约束。
- 提供仓库级打包（用于分发/共享）。

## 约定

- 打包前应优先执行校验（validate），确保生成物符合严格规则。
