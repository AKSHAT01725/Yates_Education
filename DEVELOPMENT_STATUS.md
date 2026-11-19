# Development status — FR/PM student-practice phase

## Completed in this package

- Preserved the existing AA question renderer, embedded AA question data and AA progress storage key.
- Added a dedicated FR/PM student practice page linked from the existing AA home navigation.
- Imported 96 FR (F7) and 126 PM (F5) question-level records from the supplied papers: 222 total.
- Added Section A, Section B and Section C question navigation, shared Section B scenario context, objective answer checking where a key is available, written response capture, model-answer reveal where supplied, retry, bookmarks, paper review and subject-specific progress summaries.
- Added separate FR and PM browser progress state and subject-specific Firebase document paths.
- Added Firestore rules for isolated `FR` and `PM` subject-progress documents without changing the AA progress document path.
- Added source-page references and verification metadata to every imported record.
- Kept all FR/PM questions unpublished pending academic verification.

## Imported source coverage

| Subject | Source papers | Question records | Answer text records |
|---|---:|---:|---:|
| FR / F7 | 3 | 96 | 94 |
| PM / F5 | 4 | 126 | 94 |
| Total | 7 | 222 | 188 |

PM Mock D has no matching answer PDF in the supplied assets. Two FR Mock D records do not have extracted answer text. The practice interface explicitly identifies missing answers; no missing answer is inferred.

## Automated validation

- `python tools/validate_banks.py`: passed.
- `npm run test:all`: passed, 11 tests, 0 failures.
- JavaScript syntax parsing: 4 inline executable blocks passed.
- AA baseline tests remain in place and pass.

## Still required before production release

- Academic, question-by-question comparison against the original PDFs; check all numerical data, formulas, tables, diagrams and answer mapping.
- Admin publishing workflow for approving and publishing verified FR/PM records.
- Firebase Emulator Suite tests, live Google sign-in, cross-device sync verification and production deployment of updated Firestore rules.
- Full browser-driven interaction and accessibility testing on desktop and mobile.
- Verify hosting serves the JSON banks at the expected relative paths.

The new student interface is implemented, but the imported content and cloud sync are not certified for production until the remaining checks above are completed.


## Historical follow-up enhancement (2026-11-19; session console subsequently removed)
- Added 10 original supplementary MCQs each to AA, FR and PM; source past-paper content is kept separate and clearly labelled.
- AA bank now contains 324 objective questions (314 existing + 10 original supplementary); FR contains 106 and PM contains 136.
- Added shared glassmorphism student session console on AA and FR/PM pages with searchable subject/student/computer selection, date, time slot, duration, countdown, and active/ended status.
- Added responsive animation and reduced-motion handling. Session details are local-browser only; no live attendance backend was configured.
- Academic review of original and transcribed items remains required before formal release.


## Latest change — mock workflow and common doubt board
- Removed the computer identification, student selection, session booking and countdown console from all student pages. The modern animation/design layer remains.
- Added admin PDF mock upload with PDF.js text extraction and Tesseract OCR fallback for scanned pages, numbered-question splitting, A–D option detection, editable draft review, and explicit publish/unpublish controls.
- Added student mock invitations, timed question interface, saved submissions, admin per-question marking, and individual result release.
- Added a shared real-time Common Doubts board across AA, F5 and F7; all signed-in students can read/post, and admin tutor replies appear in the shared feed.
- Added Firestore collection rules and `storage.rules`; these rules must be deployed to Firebase before the new online workflows can work.
- Important: automated PDF splitting is heuristic and all imported question text/options/marks must be checked by the admin before publication. OCR needs internet access and a readable scan.
