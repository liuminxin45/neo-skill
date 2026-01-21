# pnpm（workspace）落地片段

## 目标命令契约（建议统一）
- `pnpm -r lint`
- `pnpm -r typecheck`
- `pnpm -r test`
- `pnpm -r depcheck`

## 兼容性说明
- 如果仓库当前无法使用 `pnpm -r`：
  - 允许先在 root 提供等价聚合命令
  - 或先补齐 workspace/脚本约定，再逐步收紧 gate
