#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");

const PACKAGE_ROOT = path.resolve(__dirname, "..");
const SKILLS_ROOT = path.join(PACKAGE_ROOT, "skills");

function readPackageJson() {
  const packagePath = path.join(PACKAGE_ROOT, "package.json");
  return JSON.parse(fs.readFileSync(packagePath, "utf8"));
}

function usage() {
  const version = readPackageJson().version;
  return [
    `neo-skill ${version}`,
    "",
    "Usage:",
    "  neo-skill install [--target <path>] [--dry-run]",
    "  neo-skill list",
    "  neo-skill --version",
    "  neo-skill --help",
    "",
    "Examples:",
    "  npx neo-skill install",
    "  npx neo-skill install --target ./tmp/codex-skills",
    "  npx neo-skill list",
  ].join("\n");
}

function defaultCodexSkillsRoot() {
  const home = process.env.USERPROFILE || process.env.HOME || os.homedir();
  if (!home) {
    throw new Error("Cannot resolve home directory for Codex skills install.");
  }
  return path.resolve(home, ".codex", "skills");
}

function listSkills() {
  if (!fs.existsSync(SKILLS_ROOT)) {
    throw new Error(`Missing skills directory: ${SKILLS_ROOT}`);
  }
  return fs.readdirSync(SKILLS_ROOT, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function ensureInsideRoot(root, candidate) {
  const resolvedRoot = path.resolve(root);
  const resolvedCandidate = path.resolve(candidate);
  const relative = path.relative(resolvedRoot, resolvedCandidate);
  if (relative === "" || (!relative.startsWith("..") && !path.isAbsolute(relative))) {
    return;
  }
  throw new Error(`Refusing to write outside target root: ${resolvedCandidate}`);
}

function copyDirectory(source, target) {
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.cpSync(source, target, {
    recursive: true,
    force: true,
    errorOnExist: false,
  });
}

function removeDirectory(targetRoot, target) {
  ensureInsideRoot(targetRoot, target);
  if (fs.existsSync(target)) {
    fs.rmSync(target, { recursive: true, force: true });
  }
}

function parseInstallArgs(args) {
  const options = {
    dryRun: false,
    target: null,
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--dry-run") {
      options.dryRun = true;
    } else if (arg === "--target") {
      const value = args[index + 1];
      if (!value) {
        throw new Error("Missing value for --target.");
      }
      options.target = value;
      index += 1;
    } else if (arg.startsWith("--target=")) {
      options.target = arg.slice("--target=".length);
    } else {
      throw new Error(`Unknown install option: ${arg}`);
    }
  }

  return options;
}

function install(args) {
  const options = parseInstallArgs(args);
  const targetRoot = path.resolve(options.target || defaultCodexSkillsRoot());
  const skills = listSkills();

  if (skills.length === 0) {
    throw new Error("No skills found to install.");
  }

  console.log(`Installing ${skills.length} skill(s) to ${targetRoot}`);

  if (options.dryRun) {
    for (const skill of skills) {
      console.log(`  [dry-run] ${skill} -> ${path.join(targetRoot, skill)}`);
    }
    return;
  }

  fs.mkdirSync(targetRoot, { recursive: true });
  for (const skill of skills) {
    const source = path.join(SKILLS_ROOT, skill);
    const target = path.join(targetRoot, skill);
    ensureInsideRoot(targetRoot, target);
    removeDirectory(targetRoot, target);
    copyDirectory(source, target);
    console.log(`  Installed ${skill}`);
  }
}

function printList() {
  for (const skill of listSkills()) {
    console.log(skill);
  }
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  try {
    if (!command || command === "--help" || command === "-h") {
      console.log(usage());
      return;
    }

    if (command === "--version" || command === "-v") {
      console.log(readPackageJson().version);
      return;
    }

    if (command === "list") {
      printList();
      return;
    }

    if (command === "install") {
      install(args.slice(1));
      return;
    }

    throw new Error(`Unknown command: ${command}`);
  } catch (error) {
    console.error(`neo-skill: ${error.message}`);
    process.exit(1);
  }
}

main();
