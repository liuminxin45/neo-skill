#!/usr/bin/env node

const { spawnSync } = require("child_process");
const path = require("path");

function main() {
  const pkgRoot = path.resolve(__dirname, "..");
  const srcPath = path.join(pkgRoot, "src");
  
  // Build environment with PYTHONPATH
  const env = { ...process.env };
  const sep = process.platform === "win32" ? ";" : ":";
  env.PYTHONPATH = env.PYTHONPATH ? `${srcPath}${sep}${env.PYTHONPATH}` : srcPath;

  const pyArgs = ["-m", "omni_skill.cli", ...process.argv.slice(2)];

  // Try python first
  let result = spawnSync("python", pyArgs, { stdio: "inherit", env, shell: true });
  
  // If python not found on Windows, try py
  if (result.error && process.platform === "win32") {
    result = spawnSync("py", pyArgs, { stdio: "inherit", env, shell: true });
  }

  if (result.error) {
    console.error("neo-skill: Python not found. Please install Python 3.8+ and ensure 'python' is on PATH.");
    process.exit(127);
  }

  process.exit(result.status ?? 1);
}

main();
