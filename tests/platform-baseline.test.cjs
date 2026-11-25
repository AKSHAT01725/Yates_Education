'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const admin = fs.readFileSync(path.join(root, 'admin.html'), 'utf8');
const rules = fs.readFileSync(path.join(root, 'firestore.rules'), 'utf8');

function dataset() {
  const match = html.match(/<script\b(?=[^>]*\bid=["']kit["'])(?=[^>]*\btype=["']application\/json["'])[^>]*>([\s\S]*?)<\/script>/i);
  assert.ok(match, 'embedded question data script #kit exists');
  return JSON.parse(match[1]);
}

test('student and administrator entry points are present', () => {
  assert.match(html, /<main\s+id=["']app["']/i);
  assert.match(admin, /<html/i);
  assert.match(html, /data-tab=["']home["']/);
  assert.match(html, /data-tab=["']report["']/);
});

test('embedded AA question bank parses and has unique identifiers', () => {
  const data = dataset();
  assert.ok(Array.isArray(data.questions) && data.questions.length > 0);
  assert.ok(Array.isArray(data.scenarios) && data.scenarios.length > 0);
  assert.ok(Array.isArray(data.b) && data.b.length > 0);
  const ids = data.questions.map(q => String(q.n));
  assert.equal(new Set(ids).size, ids.length, 'Section A question numbers are unique');
  const scenarioIds = new Set(data.scenarios.map(s => String(s.id)));
  for (const q of data.questions) assert.ok(scenarioIds.has(String(q.scenario)), `question ${q.n} references a known scenario`);
});

test('core practice engine capabilities remain wired in the source', () => {
  for (const fn of ['startSession', 'renderPractice', 'renderQuestion', 'setResp', 'isCorrect', 'finishMock', 'renderResults', 'renderReport']) {
    assert.match(html, new RegExp(`function\\s+${fn}\\s*\\(`), `${fn} exists`);
  }
  for (const feature of ['data-act="flag"', 'data-act="check"', 'data-act="mock"', 'data-act="review"']) {
    assert.ok(html.includes(feature), `${feature} action exists`);
  }
});

test('timer restoration is based on a persisted absolute end timestamp', () => {
  assert.match(html, /end:\s*opts\.minutes\s*\?\s*Date\.now\(\)\s*\+\s*opts\.minutes\s*\*\s*60000/);
  assert.match(html, /Math\.max\(0,\s*ses\.end\s*-\s*Date\.now\(\)\)/);
});

test('weekly dashboard visualisation derives only from real attempt records', () => {
  assert.match(html, /function weeklyLearningPulse\s*\(/);
  assert.match(html, /\(ST\.log\s*\|\|\s*\[\]\)\.filter/);
  assert.match(html, /function renderLearningPulse\s*\(/);
  assert.match(html, /aria-label=\\?"Daily practice attempts over the last seven days/);
});

test('design layer includes keyboard focus, responsive and reduced-motion support', () => {
  assert.match(html, /:focus-visible/);
  assert.match(html, /@media\s*\(max-width:\s*760px\)/);
  assert.match(html, /prefers-reduced-motion:\s*reduce/);
});

test('Firestore policy has a signed-in check and explicit admin policy', () => {
  assert.match(rules, /function\s+signedIn\s*\(/);
  assert.match(rules, /function\s+isAdmin\s*\(/);
  assert.match(rules, /allow\s+read,\s*write:\s*if\s+owns\(uid\)\s*\|\|\s*isAdmin\(\)/);
});

test('question bank uses the six implemented Section A answer formats', () => {
  const data = dataset();
  const supported = new Set(['single', 'single-table', 'multi', 'matrix', 'columns', 'numeric']);
  const seen = new Set(data.questions.map(q => q.type));
  assert.deepEqual([...seen].sort(), [...supported].sort());
  for (const q of data.questions) {
    assert.ok(Object.hasOwn(q, 'answer'), `question ${q.n} has a marking key`);
    if (q.type === 'multi') assert.ok(Array.isArray(q.answer), `multi ${q.n} has an array answer`);
    if (q.type === 'matrix') assert.ok(Array.isArray(q.rows) && Array.isArray(q.answer), `matrix ${q.n} has rows and answers`);
    if (q.type === 'columns') assert.ok(Array.isArray(q.choices) && Array.isArray(q.answer), `columns ${q.n} has choices and answers`);
    if (q.type === 'numeric') assert.ok(typeof q.answer === 'number' || Array.isArray(q.cells), `numeric ${q.n} has numeric marking data`);
  }
  for (const type of supported) assert.match(html, new RegExp(`case ['"]${type}['"]`), `${type} marking branch exists`);
});

test('written response section retains its tutor-marking data structure', () => {
  const data = dataset();
  for (const q of data.b) {
    assert.ok(q.title && q.topic && Number(q.marks) > 0, `written question ${q.n} has title, topic and marks`);
    assert.ok(Array.isArray(q.blocks), `written question ${q.n} has requirement blocks`);
  }
  assert.match(html, /function\s+bSubmit\s*\(/);
  assert.match(html, /function\s+bApplyGrades\s*\(/);
});


test('FR and PM banks are isolated, populated, and withheld from verified publishing', () => {
  const expected = { fr: 106, pm: 136 };
  const expectedAnswers = { fr: 104, pm: 104 };
  for (const code of ['fr', 'pm']) {
    const bank = JSON.parse(fs.readFileSync(path.join(root, 'data', 'question-banks', `${code}.json`), 'utf8'));
    assert.equal(bank.subject, code.toUpperCase());
    assert.equal(bank.published, false);
    assert.equal(bank.questions.length, expected[code]);
    assert.equal(bank.questions.filter(q => q.paper.endsWith('Additional Practice Set 1')).length, 10);
    assert.equal(bank.questions.filter(q => q.answerAvailable).length, expectedAnswers[code]);
    const ids = bank.questions.map(q => q.id);
    assert.equal(new Set(ids).size, ids.length, `${code} IDs unique`);
    for (const q of bank.questions) {
      assert.equal(q.subject, code.toUpperCase());
      assert.equal(q.verification.status === 'verified', false);
      assert.ok(q.source.questionPages.length > 0);
      assert.ok(q.content.questionText);
    }
  }
  const fr = JSON.parse(fs.readFileSync(path.join(root, 'data', 'question-banks', 'fr.json'), 'utf8'));
  const frMockD = fr.questions.filter(q => q.paper.startsWith('FR Mock D'));
  assert.equal(frMockD.filter(q => !q.answerAvailable).length, 2);
  const pm = JSON.parse(fs.readFileSync(path.join(root, 'data', 'question-banks', 'pm.json'), 'utf8'));
  const mockD = pm.questions.filter(q => q.paper.startsWith('PM Mock D'));
  assert.equal(mockD.length, 32);
  assert.ok(mockD.every(q => !q.answerAvailable), 'PM Mock D has no supplied answer paper');
  const schema = JSON.parse(fs.readFileSync(path.join(root, 'data', 'question-banks', 'question.schema.json'), 'utf8'));
  assert.ok(schema.properties.subject.enum.includes('FR'));
  assert.ok(schema.properties.subject.enum.includes('PM'));
  assert.ok(schema.properties.verification.properties.status.enum.includes('needs_review'));
});

test('FR/PM student practice adapter provides section navigation, bookmarks, review and subject-isolated Firebase paths', () => {
  const page = fs.readFileSync(path.join(root, 'fr-pm-practice.html'), 'utf8');
  for (const feature of ['function appHome()', 'function drawQuestion()', 'function reviewPaper()', 'function appBookmarks()', 'subjectPractice', 'data-go=', 'data-opt=']) {
    assert.ok(page.includes(feature), `practice feature ${feature} exists`);
  }
  assert.match(page, /subjectPractice',subject/);
  assert.match(page, /attempts:\{\},bookmarks:\{\},responses:\{\}/);
});

test('three-subject supplementary questions remain and removed session station controls stay absent', () => {
  const data = dataset();
  assert.equal(data.questions.filter(q => q.source === 'Yates Education original supplementary practice set 1').length, 10);
  assert.doesNotMatch(html, /id=\"sessionConsole\"/);
  assert.doesNotMatch(html, /session-station\.js/);
  const frpm = fs.readFileSync(path.join(root, 'fr-pm-practice.html'), 'utf8');
  assert.doesNotMatch(frpm, /id=\"sessionConsole\"/);
  assert.doesNotMatch(frpm, /session-station\.js/);
  for (const code of ['fr','pm']) { const bank = JSON.parse(fs.readFileSync(path.join(root, 'data', 'question-banks', `${code}.json`), 'utf8')); assert.equal(bank.questions.filter(q => q.paper.endsWith('Additional Practice Set 1')).length, 10); }
});

test('shared mock exam workflow and cross-subject public doubt board are wired', () => {
  const extra = fs.readFileSync(path.join(root, 'student-extras.js'), 'utf8');
  for (const feature of ['refreshMocks', 'startMock', 'submitMock', 'showMyResults', 'openDoubts', 'onSnapshot', 'mockAttempts', 'commonDoubts']) assert.ok(extra.includes(feature), `student feature ${feature} exists`);
  for (const feature of ['extractMock', 'parseMockLines', 'publishMock', 'markMock', 'releaseMock', 'replyDoubt']) assert.ok(admin.includes(feature), `admin feature ${feature} exists`);
  assert.match(rules, /match \/mocks\/\{mockId\}/);
  assert.match(rules, /match \/mockAttempts\/\{attemptId\}/);
  assert.match(rules, /match \/commonDoubts\/\{doubtId\}/);
  assert.ok(fs.existsSync(path.join(root, 'storage.rules')));
});

test('new subject portal links to all three paper experiences', () => {
  const portal = fs.readFileSync(path.join(root, 'subjects.html'), 'utf8');
  assert.match(portal, /href="index\.html"/);
  assert.match(portal, /href="fr-pm-practice\.html\?subject=FR"/);
  assert.match(portal, /href="fr-pm-practice\.html\?subject=PM"/);
  assert.match(portal, /data\/question-banks\/fr\.json/);
  assert.match(portal, /data\/question-banks\/pm\.json/);
});
