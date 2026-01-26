# skill-finder 安装模式

## 两种安装模式

### 模式 1: 自动安装（默认）
- 执行 `package.install.auto_install_cmd`
- 捕获输出并记录结果
- 写入 install_record (executed=true)

### 模式 2: 手动安装
- 输出 `package.install.manual_install_cmd`
- 记录指令 (executed=false, result=skipped)
- 任务结束，不执行安装
