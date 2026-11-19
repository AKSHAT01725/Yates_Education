'use strict';
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const root = path.resolve(__dirname, '..');
const files = ['index.html', 'admin.html', 'fr-pm-practice.html'];
const externalScripts = ['student-extras.js'];
let checked = 0;
for (const file of files) {
  const html = fs.readFileSync(path.join(root, file), 'utf8');
  const scripts = [...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)];
  for (const [, attrs, body] of scripts) {
    if (/\bsrc\s*=/.test(attrs) || /application\/json/i.test(attrs) || !body.trim()) continue;
    const ext = /type\s*=\s*["']module["']/i.test(attrs) ? '.mjs' : '.js';
    const tmp = path.join(os.tmpdir(), `aa-inline-${process.pid}-${checked}${ext}`);
    fs.writeFileSync(tmp, body);
    const result = spawnSync(process.execPath, ['--check', tmp], { encoding: 'utf8' });
    fs.rmSync(tmp, { force: true });
    if (result.status !== 0) {
      process.stderr.write(`Syntax error in ${file}:\n${result.stderr || result.stdout}`);
      process.exit(result.status || 1);
    }
    checked++;
  }
}
for (const file of externalScripts) { const result = spawnSync(process.execPath, ['--check', path.join(root,file)], {encoding:'utf8'}); if(result.status!==0){process.stderr.write(`Syntax error in ${file}:\n${result.stderr||result.stdout}`);process.exit(result.status||1);} checked++; }
console.log(`PASS: ${checked} inline/external executable JavaScript block(s) parsed successfully across student/admin pages.`);
