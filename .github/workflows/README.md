# .github/workflows

本目录存放 GitHub Actions 的工作流定义（CI/CD）。

## 包含内容

- **ci.yml**：用于校验 `bin/*.js` 语法、执行 `npm pack`，并在 `main` 分支推送时（若版本未发布）执行 `npm publish`。

## 约定

- 工作流应保持可重复、可审计，不依赖仓库外的隐式状态。
- 发布相关步骤仅在受控条件下运行（例如仅 `main` 分支 + secrets）。
