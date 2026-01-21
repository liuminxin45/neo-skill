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

function runUiproCommand(args) {
  const cmd = process.platform === "win32" ? "uipro.cmd" : "uipro";
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
  return true;
}

function handleInit() {
  const pkgRoot = path.resolve(__dirname, "..");
  const cwd = process.cwd();
  
  const skillDirs = [".claude", ".windsurf", ".cursor", ".github"];
  
  console.log("Initializing skills in:", cwd);
  
  for (const dir of skillDirs) {
    const src = path.join(pkgRoot, dir);
    const dest = path.join(cwd, dir);
    
    if (!fs.existsSync(src)) {
      console.log(`  Skipping ${dir} (not found in package)`);
      continue;
    }
    
    if (fs.existsSync(dest)) {
      console.log(`  Merging ${dir} (already exists)`);
    } else {
      console.log(`  Creating ${dir}`);
    }
    
    copyDirRecursive(src, dest);
  }
  
  console.log("\nDone! neo-skills have been initialized.");
  
  console.log("\nRunning uipro init --ai all...");
  runUiproCommand(["init", "--ai", "all"]);
}

function handleUpdate() {
  console.log("Running uipro update...");
  runUiproCommand(["update"]);
}

function main() {
  const args = process.argv.slice(2);
  
  if (args[0] === "init") {
    handleInit();
    return;
  }
  
  if (args[0] === "update") {
    handleUpdate();
    return;
  }
  
  const pkgRoot = path.resolve(__dirname, "..");
  const pySrc = path.join(pkgRoot, "src");

  const env = { ...process.env };
  env.PYTHONPATH = env.PYTHONPATH ? `${pySrc}${path.delimiter}${env.PYTHONPATH}` : pySrc;

  const baseArgs = ["-m", "omni_skill.cli", ...process.argv.slice(2)];

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
