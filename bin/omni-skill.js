#!/usr/bin/env node

const { spawnSync } = require("child_process");
const path = require("path");
const fs = require("fs");

function copyDirRecursive(src, dest) {
  if (!fs.existsSync(src)) return;

  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function syncDirReplace(src, dest) {
  if (!fs.existsSync(src)) return;

  if (!fs.existsSync(dest)) {
    fs.mkdirSync(dest, { recursive: true });
  }

  const entries = fs.readdirSync(src, { withFileTypes: true });
  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);

    fs.rmSync(destPath, { recursive: true, force: true });
    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function runUiproCommand(args) {
  const cmd = "uipro";
  const result = spawnSync(cmd, args, { stdio: "inherit", shell: true });

  if (result.error) {
    const msg = String(result.error.message || "").toLowerCase();
    if (msg.includes("enoent")) {
      console.log("\nNote: uipro-cli not found. Run 'npm install -g uipro-cli' to install it.");
      return false;
    }
    console.error("Error running uipro:", result.error);
    return false;
  }
  if (typeof result.status === "number" && result.status !== 0) {
    return false;
  }
  return true;
}

function handleInit() {
  const pkgRoot = path.resolve(__dirname, "..");
  const cwd = process.cwd();

  const syncPairs = [
    { src: "skills", dest: "skills" },
    { src: path.join(".shared", "skill-creator"), dest: path.join(".shared", "skill-creator") },
    { src: path.join(".claude", "skills"), dest: path.join(".claude", "skills") },
    { src: path.join(".windsurf", "workflows"), dest: path.join(".windsurf", "workflows") },
    { src: path.join(".cursor", "commands"), dest: path.join(".cursor", "commands") },
    { src: path.join(".github", "skills"), dest: path.join(".github", "skills") },
  ];

  console.log("Initializing skills in:", cwd);

  for (const p of syncPairs) {
    const src = path.join(pkgRoot, p.src);
    const dest = path.join(cwd, p.dest);

    if (!fs.existsSync(src)) {
      console.log(`  Skipping ${p.dest} (not found in package)`);
      continue;
    }

    console.log(`  Syncing ${p.dest} (replace items)`);
    syncDirReplace(src, dest);
  }

  console.log("\nDone! neo-skills have been initialized.");

  if (String(process.env.NEO_SKILLS_SKIP_UIPRO_INIT || "").trim() === "1") {
    console.log("\nSkipping uipro init (NEO_SKILLS_SKIP_UIPRO_INIT=1)");
    return;
  }

  console.log("\nRunning uipro init --ai all...");
  runUiproCommand(["init", "--ai", "all"]);
}

function handleUpdate() {
  console.log("Running uipro update...");
  return runUiproCommand(["update"]) ? 0 : 1;
}

function runPythonCommand(baseArgs, env) {
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
      return 1;
    }
    return r.status == null ? 1 : r.status;
  }

  console.error(
    "Python not found. Please install Python 3 and ensure 'python' works, or set OMNI_SKILL_PYTHON to your interpreter path."
  );
  if (lastError) {
    console.error(lastError);
  }
  return 127;
}

function main() {
  const args = process.argv.slice(2);

  if (args[0] === "init") {
    handleInit();
    return;
  }

  if (args[0] === "update") {
    const pkgRoot = path.resolve(__dirname, "..");
    const pySrc = path.join(pkgRoot, "src");

    const env = { ...process.env };
    env.PYTHONPATH = env.PYTHONPATH ? `${pySrc}${path.delimiter}${env.PYTHONPATH}` : pySrc;

    const baseArgs = ["-m", "omni_skill.cli", ...process.argv.slice(2)];
    const pyStatus = runPythonCommand(baseArgs, env);
    if (pyStatus !== 0) {
      process.exit(pyStatus);
    }

    const uiproStatus = handleUpdate();
    process.exit(uiproStatus);
  }

  const pkgRoot = path.resolve(__dirname, "..");
  const pySrc = path.join(pkgRoot, "src");

  const env = { ...process.env };
  env.PYTHONPATH = env.PYTHONPATH ? `${pySrc}${path.delimiter}${env.PYTHONPATH}` : pySrc;

  const baseArgs = ["-m", "omni_skill.cli", ...process.argv.slice(2)];

  const status = runPythonCommand(baseArgs, env);
  process.exit(status);
}

main();
