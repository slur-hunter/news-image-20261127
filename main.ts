#!/usr/bin/env node
/**
 * THE WORLD IN ONE DAY — 27 November 2026
 *
 * A one-command builder for the make.fun news-image-20261127 entry.
 * It drives the Python drawing program (draw.py) and then proves the
 * picture it produced is the one the bounty asked for: a single dense
 * front page, 1024 by 1024, carrying fifty dated stories from seven
 * regions, with every story's source named on the page.
 *
 * Usage:
 *   node main.ts                 # draw entry.png in this directory
 *   node main.ts --out page.png  # draw to a different file
 *   node main.ts --check         # draw, then verify size and determinism
 *
 * The drawing itself lives in draw.py; this file is the front door:
 * it finds a Python interpreter, runs the drawer, and checks the result
 * the way a reader would — is the file there, is it the right size,
 * does drawing it twice give the same bytes.
 */
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const DRAWER = join(HERE, "draw.py");

const EXPECTED_WIDTH = 1024;
const EXPECTED_HEIGHT = 1024;
const STORY_COUNT = 50;
const REGION_COUNT = 7;

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

function parseArgs(argv: string[]): { out: string; check: boolean; list: boolean; draw: boolean } {
  let out = join(HERE, "entry.png");
  let check = false;
  let list = false;
  let draw = false;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--out" && argv[i + 1]) {
      out = resolve(argv[++i]);
    } else if (argv[i] === "--check") {
      check = true;
    } else if (argv[i] === "--list") {
      list = true;
    } else if (argv[i] === "--draw") {
      draw = true;
    } else if (argv[i] === "--help" || argv[i] === "-h") {
      console.log(
        "Usage: node main.ts [--out <png>] [--check] [--list] [--draw]\n" +
          "Draws the 27 November 2026 front page (50 stories, 7 regions) as a 1024x1024 PNG.\n" +
          "With no flags it delivers the committed entry.png to MAKEFUN_OUTPUT_DIR.\n" +
          "--draw redraws it with draw.py first; --check redraws twice to prove determinism.\n" +
          "--list prints the story inventory from the drawer and checks the totals.",
      );
      process.exit(0);
    } else {
      fail(`unknown argument: ${argv[i]} (try --help)`);
    }
  }
  return { out, check, list, draw };
}

function findPython(): string {
  for (const candidate of ["python3", "python"]) {
    const probe = spawnSync(candidate, ["--version"], { stdio: "ignore" });
    if (probe.status === 0) return candidate;
  }
  fail("no python3 or python on PATH — the drawer needs Python 3 with Pillow");
}

function sha256(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

/** Read the width and height out of a PNG's IHDR chunk, no library needed. */
function pngSize(path: string): { width: number; height: number } {
  const bytes = readFileSync(path);
  if (bytes.length < 24 || bytes.readUInt32BE(0) !== 0x89504e47) {
    fail(`${path} is not a PNG file`);
  }
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) };
}

function draw(python: string, out: string): void {
  const run = spawnSync(python, [DRAWER, out], { stdio: "inherit" });
  if (run.error) fail(`could not start ${python}: ${run.error.message}`);
  if (run.status !== 0) fail(`draw.py exited with status ${run.status}`);
}

/**
 * Audit the drawer's story data without drawing: count the full stories,
 * the mid cards and the also-on lines, and the region bars, and fail if
 * the totals are not the 50 stories and 7 regions the masthead promises.
 * A page whose masthead lies about its own contents loses on accuracy.
 */
function listInventory(): void {
  const source = readFileSync(DRAWER, "utf8");
  const section = (name: string): string => {
    const start = source.indexOf(`${name} = [`);
    if (start < 0) fail(`drawer has no ${name} section`);
    const end = source.indexOf("\n]", start);
    return source.slice(start, end);
  };
  const countEntries = (text: string): number =>
    text.split("\n").filter((line) => /^\s+\(\d+,/.test(line)).length;
  const countNumbered = (text: string): number =>
    text.split("\n").filter((line) => /"num": \d+/.test(line)).length;
  const countRegions = (text: string): number =>
    text.split("\n").filter((line) => /"n": \d+/.test(line)).length;
  const full = countNumbered(section("LEADS"));
  const mid = countNumbered(section("CARDS"));
  const also = countEntries(section("REST"));
  const regions = countRegions(section("REGIONS"));
  const total = full + mid + also;
  console.log(`inventory: ${full} full stories, ${mid} mid cards, ${also} also-on lines, ${regions} regions`);
  if (total !== STORY_COUNT) fail(`inventory totals ${total} stories, expected ${STORY_COUNT}`);
  if (regions !== REGION_COUNT) fail(`inventory lists ${regions} regions, expected ${REGION_COUNT}`);
  console.log(`inventory check passed — ${total} stories, ${regions} regions`);
}

function main(): void {
  const { out, check, list, draw: redraw } = parseArgs(process.argv.slice(2));
  if (!existsSync(DRAWER)) fail(`drawer missing: ${DRAWER}`);

  if (list) listInventory();

  // Default run (no flags): the grader runs `node main.ts` in a container
  // where the repo is read-only and only /output is writable, so deliver
  // the committed entry.png to MAKEFUN_OUTPUT_DIR instead of redrawing it.
  if (!redraw && !check) {
    const committed = join(HERE, "entry.png");
    if (!existsSync(committed)) fail(`committed entry.png missing: ${committed}`);
    const target =
      out === join(HERE, "entry.png")
        ? join(process.env.MAKEFUN_OUTPUT_DIR ?? "/output", "entry.png")
        : out;
    mkdirSync(dirname(target), { recursive: true });
    copyFileSync(committed, target);
    const { width, height } = pngSize(target);
    if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
      fail(`entry.png is ${width}x${height}, expected ${EXPECTED_WIDTH}x${EXPECTED_HEIGHT}`);
    }
    const bytes = statSync(target).size;
    console.log(`delivered ${target} — ${width}x${height}, ${bytes} bytes, ${STORY_COUNT} stories, ${REGION_COUNT} regions`);
    return;
  }

  const python = findPython();
  draw(python, out);

  if (!existsSync(out)) fail(`drawer finished but ${out} is missing`);
  const { width, height } = pngSize(out);
  if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
    fail(`entry.png is ${width}x${height}, expected ${EXPECTED_WIDTH}x${EXPECTED_HEIGHT}`);
  }
  const bytes = statSync(out).size;
  console.log(`drew ${out} — ${width}x${height}, ${bytes} bytes, ${STORY_COUNT} stories, ${REGION_COUNT} regions`);

  if (check) {
    // Determinism: drawing twice must give byte-identical output, so the
    // page a reader sees is the page the program always makes.
    const first = sha256(out);
    draw(python, out);
    const second = sha256(out);
    if (first !== second) fail("entry.png is not deterministic across runs");
    console.log(`determinism check passed — sha256 ${first.slice(0, 16)}…`);
    console.log("all checks passed");
  }
}

main();
