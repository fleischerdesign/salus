import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs';
import { join, extname } from 'node:path';

const FRONTEND_SRC = new URL('../src/', import.meta.url).pathname;
const BACKEND_SRC = new URL('../../src/salus/', import.meta.url).pathname;
const ICONS_JSON = new URL('../src/lib/icons.json', import.meta.url).pathname;
const FULL_SET = new URL('../node_modules/@iconify-json/material-symbols/icons.json', import.meta.url).pathname;

// Matches name="icon-name" or icon: 'icon-name' or icon="icon-name"
const ICON_NAME_RE = /\b(?:name|icon)\s*[=:]\s*['"]([a-z0-9][a-z0-9-]+)['"]/g;

// Matches the icon field inside DEFAULT_METRIC_TYPES tuples in metric_type_mapping.py
// Each tuple entry has the icon as the 6th string literal: ("Name", "unit", ..., "icon-name", ...)
const METRIC_TYPE_ICON_RE = /['"]([a-z0-9][a-z0-9-]+)['"]\s*,\s*['"](?:small|medium|large)['"]\s*,\s*(?:True|False)/g;

const SKIP_NAMES = new Set([
  'name', 'label', 'value', 'password', 'username', 'email',
  'metric', 'exercise', 'reps', 'rpe', 'weight', 'unit', 'target',
  'direction', 'frequency', 'timeframe', 'equipment', 'muscles',
  'notes', 'size', 'handle', 'lat', 'lon', 'tz', 'viewport',
  'file', 'theme', 'icon', 'new', 'current', 'progress',
  'chronotype', 'multiselect', 'edit-size',
  'systolic', 'diastolic', 'deadline', 'instructions', 'locale', 'timestamp',
]);

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) {
      out.push(...walk(full));
    } else if (['.svelte', '.ts', '.js'].includes(extname(full))) {
      out.push(full);
    }
  }
  return out;
}

function extractIconNames() {
  const names = new Set();

  // 1. Scan frontend source for icon="..." / name="..." references
  for (const file of walk(FRONTEND_SRC)) {
    if (file.endsWith('icons.json') || file.includes('node_modules')) continue;
    const src = readFileSync(file, 'utf8');
    for (const match of src.matchAll(ICON_NAME_RE)) {
      const name = match[1];
      if (SKIP_NAMES.has(name)) continue;
      names.add(name);
    }
  }

  // 2. Scan backend DEFAULT_METRIC_TYPES for DB-stored icon names
  const mappingPath = join(BACKEND_SRC, 'services', 'metric_type_mapping.py');
  const mappingSrc = readFileSync(mappingPath, 'utf8');
  for (const match of mappingSrc.matchAll(METRIC_TYPE_ICON_RE)) {
    names.add(match[1]);
  }

  return [...names].sort();
}

function buildSubset(names, fullSet) {
  const icons = {};
  const missing = [];

  for (const name of names) {
    if (name in fullSet.icons) {
      icons[name] = fullSet.icons[name];
    } else if (name in (fullSet.aliases || {})) {
      const parent = fullSet.aliases[name].parent;
      if (parent in fullSet.icons) {
        icons[name] = fullSet.icons[parent];
      } else if (parent in fullSet.aliases) {
        let p = parent;
        while (p in fullSet.aliases && !(p in fullSet.icons)) {
          p = fullSet.aliases[p].parent;
        }
        if (p in fullSet.icons) {
          icons[name] = fullSet.icons[p];
        } else {
          missing.push(name);
        }
      } else {
        missing.push(name);
      }
    } else {
      missing.push(name);
    }
  }

  return { icons, missing };
}

const fullSet = JSON.parse(readFileSync(FULL_SET, 'utf8'));
const names = extractIconNames();
console.log(`Found ${names.length} icon references:`);
console.log(names.join(', '));

const { icons, missing } = buildSubset(names, fullSet);

if (missing.length > 0) {
  console.error('\nERROR: Icons not found in material-symbols:');
  console.error(missing.join(', '));
  process.exit(1);
}

const output = {
  prefix: 'material-symbols',
  icons,
  lastModified: Date.now(),
  width: 24,
  height: 24,
};

writeFileSync(ICONS_JSON, JSON.stringify(output) + '\n');
console.log(`\nWrote ${Object.keys(icons).length} icons to ${ICONS_JSON}`);
