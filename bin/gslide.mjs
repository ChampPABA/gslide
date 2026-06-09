#!/usr/bin/env node

import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const pkgRoot = join(__dirname, "..");
const venvBin = join(pkgRoot, ".venv", "bin");
const gslideExe = join(venvBin, "gslide");

if (!existsSync(gslideExe)) {
  console.error("gslide Python package not installed.");
  console.error("Run: npm rebuild @champpaba/gslide");
  process.exit(1);
}

const args = process.argv.slice(2);
const child = spawn(gslideExe, args, {
  stdio: "inherit",
  env: { ...process.env, PATH: `${venvBin}:${process.env.PATH}` },
});

child.on("close", (code) => process.exit(code ?? 1));
child.on("error", (err) => {
  console.error(`Failed to start gslide: ${err.message}`);
  process.exit(1);
});
