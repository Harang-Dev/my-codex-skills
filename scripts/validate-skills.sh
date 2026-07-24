#!/usr/bin/env bash

set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

node --input-type=module - "$SOURCE_DIR" <<'NODE'
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const sourceDir = process.argv[2];
const manifestPath = join(sourceDir, 'manifest.json');
const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
const errors = [];

if (manifest.schemaVersion !== 1) {
  errors.push('manifest.schemaVersion must equal 1');
}

if (typeof manifest.version !== 'string' || !/^\d+\.\d+\.\d+$/.test(manifest.version)) {
  errors.push('manifest.version must use semantic versioning (for example, 1.0.0)');
}

if (typeof manifest.skills !== 'object' || manifest.skills === null) {
  errors.push('manifest.skills must be an object');
}

const skillDirectories = readdirSync(join(sourceDir, 'skills'), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();
const manifestSkills = Object.keys(manifest.skills ?? {}).sort();

for (const skillName of skillDirectories) {
  const skillPath = join(sourceDir, 'skills', skillName);
  const skillFile = join(skillPath, 'SKILL.md');
  const manifestSkill = manifest.skills?.[skillName];

  if (!existsSync(skillFile)) {
    errors.push(`${skillName}: SKILL.md is missing`);
    continue;
  }

  const contents = readFileSync(skillFile, 'utf8');
  const frontmatter = contents.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);

  if (!frontmatter) {
    errors.push(`${skillName}: YAML front matter is missing`);
    continue;
  }

  if (!/^name:\s*.+$/m.test(frontmatter[1])) {
    errors.push(`${skillName}: front matter requires name`);
  }

  if (!/^description:\s*.+$/m.test(frontmatter[1])) {
    errors.push(`${skillName}: front matter requires description`);
  }

  if (!manifestSkill || manifestSkill.path !== `skills/${skillName}`) {
    errors.push(`${skillName}: manifest entry must point to skills/${skillName}`);
  }
}

for (const skillName of manifestSkills) {
  const skillPath = join(sourceDir, manifest.skills[skillName].path ?? '');

  if (!existsSync(skillPath) || !statSync(skillPath).isDirectory()) {
    errors.push(`${skillName}: manifest path does not exist or is not a directory`);
  }
}

if (errors.length > 0) {
  console.error('Skill validation failed:');
  errors.forEach((error) => console.error(`- ${error}`));
  process.exit(1);
}

console.log(`Validated ${skillDirectories.length} skills (version ${manifest.version}).`);
NODE
