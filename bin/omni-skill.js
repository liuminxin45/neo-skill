#!/usr/bin/env node

const { spawnSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const STATE_FILE = ".neo-skills.json";

function readPackageVersion(pkgRoot) {
  try {
    const pkgJsonPath = path.join(pkgRoot, "package.json");
    const raw = fs.readFileSync(pkgJsonPath, "utf-8");
    const pkg = JSON.parse(raw);
    return String(pkg.version || "").trim() || "unknown";
  } catch {
    return "unknown";
  }
}

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function writeVersionFile(destBaseDir, version) {
  ensureDir(destBaseDir);
  fs.writeFileSync(path.join(destBaseDir, "VERSION"), `${version}\n`, "utf-8");
}

function writeInitState(cwd, selectedAis) {
  try {
    const statePath = path.join(cwd, STATE_FILE);
    const payload = {
      ais: selectedAis,
    };
    fs.writeFileSync(statePath, JSON.stringify(payload, null, 2) + "\n", "utf-8");
  } catch {
    // best effort
  }
}

function readInitState(cwd) {
  const statePath = path.join(cwd, STATE_FILE);
  if (!fs.existsSync(statePath)) {
    return { ok: false, error: `Missing ${STATE_FILE}. Please run: omni-skill init --ai <target>` };
  }
  try {
    const raw = fs.readFileSync(statePath, "utf-8");
    const parsed = JSON.parse(raw);
    const ais = Array.isArray(parsed.ais) ? parsed.ais.map(normalizeAiValue).filter(Boolean) : [];
    const resolved = resolveSelectedAis(ais);
    if (!resolved.ok) return resolved;
    if (resolved.selected.length === 0) {
      return { ok: false, error: `Invalid ${STATE_FILE}: ais is empty. Please re-run init.` };
    }
    return { ok: true, selected: resolved.selected };
  } catch {
    return { ok: false, error: `Invalid ${STATE_FILE}. Please delete it and re-run init.` };
  }
}

function normalizeAiValue(value) {
  return String(value || "")
    .trim()
    .toLowerCase();
}

function parseAiArgs(args) {
  const out = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--ai") {
      const v = normalizeAiValue(args[i + 1]);
      if (!v) return { ok: false, error: "Missing value for --ai" };
      out.push(v);
      i++;
    }
  }
  return { ok: true, values: out };
}

function getSupportedAis() {
  return [
    "claude",
    "cursor",
    "windsurf",
    "antigravity",
    "copilot",
    "kiro",
    "codex",
    "qoder",
    "roocode",
    "gemini",
    "trae",
    "opencode",
    "continue",
    "all",
  ];
}

function resolveSelectedAis(aiValues) {
  const supported = new Set(getSupportedAis());

  if (aiValues.length === 0) {
    return { ok: true, selected: [] };
  }

  for (const v of aiValues) {
    if (!supported.has(v)) {
      return { ok: false, error: `Unknown --ai value: ${v}` };
    }
  }

  if (aiValues.includes("all")) {
    return {
      ok: true,
      selected: getSupportedAis().filter((x) => x !== "all"),
    };
  }

  return { ok: true, selected: Array.from(new Set(aiValues)) };
}

function getAiCopyRules() {
  return {
    claude: {
      syncPairs: [{ src: path.join(".claude", "skills"), dest: path.join(".claude", "skills") }],
      baseDirs: [".claude"],
    },
    windsurf: {
      syncPairs: [{ src: path.join(".windsurf", "workflows"), dest: path.join(".windsurf", "workflows") }],
      baseDirs: [".windsurf"],
    },
    cursor: {
      syncPairs: [{ src: path.join(".cursor", "commands"), dest: path.join(".cursor", "commands") }],
      baseDirs: [".cursor"],
    },
    copilot: {
      syncPairs: [{ src: path.join(".github", "skills"), dest: path.join(".github", "skills") }],
      baseDirs: [".github"],
    },
    antigravity: {
      syncPairs: [
        { src: ".agent", dest: ".agent" },
        { src: ".shared", dest: ".shared" },
      ],
      baseDirs: [".agent", ".shared"],
    },
    kiro: {
      syncPairs: [{ src: ".kiro", dest: ".kiro" }],
      baseDirs: [".kiro"],
    },
    codex: {
      syncPairs: [{ src: ".codex", dest: ".codex" }],
      baseDirs: [".codex"],
    },
    qoder: {
      syncPairs: [{ src: ".qoder", dest: ".qoder" }],
      baseDirs: [".qoder"],
    },
    roocode: {
      syncPairs: [{ src: ".roocode", dest: ".roocode" }],
      baseDirs: [".roocode"],
    },
    gemini: {
      syncPairs: [{ src: ".gemini", dest: ".gemini" }],
      baseDirs: [".gemini"],
    },
    trae: {
      syncPairs: [{ src: ".trae", dest: ".trae" }],
      baseDirs: [".trae"],
    },
    opencode: {
      syncPairs: [{ src: ".opencode", dest: ".opencode" }],
      baseDirs: [".opencode"],
    },
    continue: {
      syncPairs: [{ src: ".continue", dest: ".continue" }],
      baseDirs: [".continue"],
    },
  };
}

function printInitHelp() {
  /* eslint-disable no-console */
  const supported = getSupportedAis().join("|");
  console.log("Usage: omni-skill init --ai <target>");
  console.log(`  <target>: ${supported}`);
  console.log("Examples:");
  console.log("  omni-skill init --ai claude");
  console.log("  omni-skill init --ai cursor");
  console.log("  omni-skill init --ai windsurf");
  console.log("  omni-skill init --ai antigravity");
  console.log("  omni-skill init --ai copilot");
  console.log("  omni-skill init --ai all");
  /* eslint-enable no-console */
}

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
      /* eslint-disable-next-line no-console */
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

function runNpmSelfUpdate() {
  if (String(process.env.NEO_SKILLS_SKIP_SELF_UPDATE || "").trim() === "1") {
    /* eslint-disable-next-line no-console */
    console.log("Skipping npm self-update (NEO_SKILLS_SKIP_SELF_UPDATE=1)");
    return true;
  }

  /* eslint-disable-next-line no-console */
  console.log("Updating neo-skills (npm -g) ...");
  const result = spawnSync("npm", ["install", "-g", "neo-skills@latest"], { stdio: "inherit", shell: true });
  if (result.error) {
    console.error("npm self-update failed:", result.error);
    return false;
  }
  if (typeof result.status === "number" && result.status !== 0) {
    console.error("npm self-update failed with exit code:", result.status);
    return false;
  }
  return true;
}

function buildSyncPairs(effectiveAis, aiRules) {
  const syncPairs = [
    { src: "skills", dest: "skills" },
    { src: path.join(".shared", "skill-creator"), dest: path.join(".shared", "skill-creator") },
  ];
  for (const ai of effectiveAis) {
    const r = aiRules[ai];
    if (r) {
      for (const p of r.syncPairs) {
        syncPairs.push(p);
      }
    }
  }
  return syncPairs;
}

function performSync(pkgRoot, cwd, syncPairs) {
  for (const p of syncPairs) {
    const src = path.join(pkgRoot, p.src);
    const dest = path.join(cwd, p.dest);
    if (!fs.existsSync(src)) {
      /* eslint-disable-next-line no-console */
      console.log(`  Skipping ${p.dest} (not found in package)`);
      continue;
    }
    /* eslint-disable-next-line no-console */
    console.log(`  Syncing ${p.dest} (replace items)`);
    syncDirReplace(src, dest);
  }
}

function writeVersionFiles(cwd, effectiveAis, aiRules, version) {
  for (const ai of effectiveAis) {
    const r = aiRules[ai];
    if (!r) continue;
    for (const baseDir of r.baseDirs) {
      writeVersionFile(path.join(cwd, baseDir), version);
    }
  }
}

function runUiproForAis(effectiveAis, mode) {
  if (mode === "update") {
    for (const ai of effectiveAis) {
      const ok = runUiproCommand(["update", "--ai", ai]);
      if (!ok) {
        /* eslint-disable-next-line no-console */
        console.log(`uipro update failed for --ai ${ai}; trying init...`);
        runUiproCommand(["init", "--ai", ai]);
      }
    }
  } else {
    for (const ai of effectiveAis) {
      runUiproCommand(["init", "--ai", ai]);
    }
  }
}

function handleInit(selectedAis, mode) {
  const pkgRoot = path.resolve(__dirname, "..");
  const cwd = process.cwd();
  const version = readPackageVersion(pkgRoot);
  const aiRules = getAiCopyRules();
  const effectiveAis = selectedAis.length ? selectedAis : getSupportedAis().filter((x) => x !== "all");

  const syncPairs = buildSyncPairs(effectiveAis, aiRules);
  /* eslint-disable-next-line no-console */
  console.log("Initializing skills in:", cwd);
  performSync(pkgRoot, cwd, syncPairs);
  writeVersionFiles(cwd, effectiveAis, aiRules, version);
  /* eslint-disable-next-line no-console */
  console.log("\nDone! neo-skills have been initialized.");

  if (mode === "init") {
    writeInitState(cwd, selectedAis);
  }

  if (String(process.env.NEO_SKILLS_SKIP_UIPRO_INIT || "").trim() === "1") {
    /* eslint-disable-next-line no-console */
    console.log("\nSkipping uipro init/update (NEO_SKILLS_SKIP_UIPRO_INIT=1)");
    return;
  }

  const verb = mode === "update" ? "update" : "init";
  /* eslint-disable-next-line no-console */
  console.log(`\nRunning uipro ${verb}...`);
  runUiproForAis(effectiveAis, mode);
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
    "Python not found. Please install Python 3 and ensure 'python' works, or set OMNI_SKILL_PYTHON to your interpreter path.",
  );
  if (lastError) {
    console.error(lastError);
  }
  return 127;
}

function main() {
  const args = process.argv.slice(2);

  const aiParse = parseAiArgs(args);
  if (!aiParse.ok) {
    console.error(aiParse.error);
    process.exit(1);
  }
  const aiResolve = resolveSelectedAis(aiParse.values);
  if (!aiResolve.ok) {
    console.error(aiResolve.error);
    printInitHelp();
    process.exit(1);
  }

  if (args[0] === "init") {
    if (aiResolve.selected.length === 0) {
      printInitHelp();
      process.exit(1);
    }
    handleInit(aiResolve.selected, "init");
    return;
  }

  if (args[0] === "update") {
    if (args.length > 1 || aiParse.values.length > 0) {
      console.error("omni-skill update does not accept any arguments.");
      process.exit(1);
    }
    runNpmSelfUpdate();
    const cwd = process.cwd();
    const state = readInitState(cwd);
    if (!state.ok) {
      console.error(state.error);
      process.exit(1);
    }
    handleInit(state.selected, "update");
    return;
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
