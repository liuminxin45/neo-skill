#!/usr/bin/env node

const { spawnSync } = require("child_process");
const path = require("path");

function main() {
  const pkgRoot = path.resolve(__dirname, "..");
  const pySrc = path.join(pkgRoot, "src");

  const env = { ...process.env };
  env.PYTHONPATH = env.PYTHONPATH ? `${pySrc}${path.delimiter}${env.PYTHONPATH}` : pySrc;

  const baseArgs = ["-m", "skill_creator.cli", ...process.argv.slice(2)];

  const candidates = [];
  if (env.OMNI_SKILL_PYTHON) {
    candidates.push({ cmd: env.OMNI_SKILL_PYTHON, extraArgs: [] });
  }
  if (process.platform === "win32") {
    candidates.push({ cmd: "python", extraArgs: [] });
    candidates.push({ cmd: "py", extraArgs: ["-3"] });
  } else {
    candidates.push({ cmd: "python3", extraArgs: [] });
    candidates.push({ cmd: "python", extraArgs: [] });
  }

  let lastError = null;
  for (const c of candidates) {
    const r = spawnSync(c.cmd, [...c.extraArgs, ...baseArgs], { stdio: "inherit", env });
    if (r.error) {
      lastError = r.error;
      const msg = String(r.error.message || "").toLowerCase();
      if (msg.includes("enoent")) {
        continue;
      }
      console.error(r.error);
      process.exit(1);
    }
    process.exit(r.status == null ? 1 : r.status);
  }

  console.error(
    "Python not found. Please install Python 3 and ensure 'python' works, or set OMNI_SKILL_PYTHON to your interpreter path."
  );
  if (lastError) {
    console.error(lastError);
  }
  process.exit(127);
}

main();
