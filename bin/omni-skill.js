#!/usr/bin/env node

const { spawn } = require("child_process");
const path = require("path");

function buildEnv(pkgRoot) {
  const env = { ...process.env };
  const srcPath = path.join(pkgRoot, "src");
  const key = process.platform === "win32" ? "PYTHONPATH" : "PYTHONPATH";
  const sep = process.platform === "win32" ? ";" : ":";
  env[key] = env[key] ? `${srcPath}${sep}${env[key]}` : srcPath;
  return env;
}

function spawnPython(cmd, args, env) {
  return spawn(cmd, args, { stdio: "inherit", env });
}

function main() {
  const pkgRoot = path.resolve(__dirname, "..");
  const env = buildEnv(pkgRoot);
  const pyArgs = ["-m", "omni_skill.cli", ...process.argv.slice(2)];

  // Try python first; if not found on Windows, try py.
  let child = spawnPython("python", pyArgs, env);

  child.on("error", (err) => {
    if (process.platform === "win32") {
      const child2 = spawnPython("py", pyArgs, env);
      child2.on("error", () => {
        console.error("neo-skill: Python not found. Please install Python 3.8+ and ensure 'python' (or 'py') is on PATH.");
        process.exit(127);
      });
      child2.on("exit", (code) => process.exit(code ?? 1));
      return;
    }

    console.error("neo-skill: Python not found. Please install Python 3.8+ and ensure 'python' is on PATH.");
    process.exit(127);
  });

  child.on("exit", (code) => process.exit(code ?? 1));
}

main();
