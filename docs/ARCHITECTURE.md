# Application architecture — incremental baseline

## Current state (Phase 3)

The supplied product retains its static AA application with a separate admin HTML entry point, and now includes a dedicated FR/PM student-practice adapter page. `index.html` contains the question-bank JSON, CSS, view rendering, practice state, timer logic, Firebase integration and local persistence. This is deliberately retained as the production baseline while tests are established; a wholesale extraction would create unnecessary regression risk.

## Current logical boundaries

| Boundary | Existing implementation | Target module boundary |
|---|---|---|
| Content catalogue | Embedded `#kit` JSON script for AA; JSON banks for FR/PM | `src/data/*-question-bank.json` + validated schema |
| Student state | AA `ST`; FR/PM subject-isolated state in `fr-pm-practice.html` | `src/state/student-state.js` |
| Practice domain | AA engine plus FR/PM question adapter with matching practice/review workflows | `src/domain/practice-engine.js` and subject adapters |
| UI rendering | AA views in `index.html`; FR/PM views in `fr-pm-practice.html` | `src/ui/views/*` and shared components |
| Persistence | Local storage + Firestore sync listeners | `src/services/persistence/*` |
| Authentication | Firebase Auth flow in student page | `src/services/auth/firebase-auth.js` |
| Administration | `admin.html` | Separate protected admin application |

These are target boundaries, not claims that those modules have already been extracted.

## Refactoring rules

1. Keep `index.html` and the embedded data as the rollback source until parity tests cover each extracted workflow.
2. Extract question data first, validate every record, and compare counts/IDs before and after extraction.
3. Extract pure domain functions before UI rendering; do not change answer semantics during the move.
4. Keep Firebase access behind a service boundary and keep authorization in Firestore rules, not UI visibility.
5. Migrate one view at a time. Keep a reversible commit/package for every migration.
6. Use schema versions and migration tests before changing persisted student state.
7. Do not expand the product to other ACCA papers by relabelling AA questions. Each paper requires verified syllabus mapping and original/licensed question content.

## Test strategy

- `npm run test:syntax`: parse inline executable scripts in the AA, admin and FR/PM student entry points.
- `npm test`: source/data regression baseline using Node's built-in test runner.
- Next gate: browser-driven Playwright tests for sign-in states, topic selection, answer marking, flags, mock timer, results, report and mobile layout.
- Separate gate: Firebase Emulator tests for student isolation, admin access and collection-level default denial.

## Known external dependencies / release gates

Firebase project configuration and authorized admin identity, Firestore rules emulator validation, real authentication, cloud sync across two devices, EmailJS delivery, PDF resource hosting, and deployment credentials require owner-controlled configuration and staging access. They are not certified by the local test suite.


## Shared mock assessments and common doubts
- `student-extras.js` mounts the cross-subject student mock invitation/results UI and Common Doubts chat board.
- Admin uploads source PDFs to Firebase Storage under `mock-pdfs/`, and writes draft metadata/questions to `mocks/{mockId}` and its `questions` subcollection.
- Student submissions are stored in `mockAttempts/{attemptId}` with answer documents in the nested `answers` subcollection. Admin assigns marks per question and releases the final score.
- `commonDoubts/{doubtId}` is the shared cross-subject discussion feed; tutor replies are written by admins and live-updated through Firestore snapshots.
- The former session-station controls and their scripts are removed from the student entry points.
