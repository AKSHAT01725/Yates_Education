# AA Exam Practice — Initial Technical Audit

**Audit date:** 14 November 2026  
**Scope:** Supplied `AA_Exam_Practice` ZIP archive; source-level inspection only.

## 1. Executive summary

The archive contains an established, single-paper ACCA Audit and Assurance practice application rather than a blank starter project. The main student application is a large self-contained `index.html`; the administrator interface is a separate `admin.html`. Educational data is embedded as JSON in the student page. Firebase Authentication/Firestore integration is present in the client code, while browser local storage is also used as local state/cache. The project includes a substantial library of PDF learning resources and one PowerPoint revision deck.

**Recommendation:** retain and incrementally refactor the existing application. Do not replace it wholesale or represent the current AA-only product as the requested 50+ page multi-paper platform. First resolve and verify backend security rules, then isolate the embedded data and application logic into testable modules before expanding the product.

## 2. Archive inventory

- 27 ZIP entries including directory entries; 22 files in the application folder.
- `index.html`: approximately 2.24 MB; 2,152 lines; student-facing app, embedded question/scenario dataset, styles and application logic.
- `admin.html`: approximately 66 KB; 760 lines; separate admin interface.
- 17 PDF files; page counts are listed below.
- `AA_revision_Slide_ch_10.pptx`: 18 slides.
- Setup/configuration notes: `FIREBASE_SETUP_GUIDE.txt`, `FIRESTORE_RULES_ADD_THIS.txt`, `EMAILJS_SETUP_GUIDE.txt`.
- No separate source tree, package manifest, automated test suite, CI configuration, or complete `firestore.rules` file was found in the archive.

### PDF inventory

| File | Pages |
|---|---:|
| `AA_BPP_exam_kit.pdf` | 552 |
| `AA_Control_Revision_Notes.pdf` | 20 |
| `AA_Notes_Ethics.pdf` | 35 |
| `AA_Pocket_Notes_2025-26.pdf` | 130 |
| `AA_Procedure_Ek_Revision_Notes.pdf` | 20 |
| `AA_Review_reporting_EK_Revision_Notes.pdf` | 7 |
| `ALL_IFRS_F7.pdf` | 2 |
| `AUDIT_RISKS_PDF.pdf` | 21 |
| `All_Bookish_knowledge_parts_in_ONE_FILE.pdf` | 30 |
| `Audit_Procedures_Simplified.pdf` | 2 |
| `Audit_TEST_OF_CONTROLS_sheet.pdf` | 37 |
| `Audit_procedures.pdf` | 20 |
| `Ch_3.pdf` | 30 |
| `Procedure_Question_Exam_kit.pdf` | 1 |
| `Review_Reporting_Writing_Notes.pdf` | 2 |
| `Review_reporting_Note.pdf` | 5 |
| `Risk_Response_Exam_kit_Q.pdf` | 3 |

## 3. Existing functionality identified

### Student application

The visible navigation includes Practice, Scoreboard, PDFs, Study Planner, ACCA Study Hub and account/cloud-save controls. The application includes Section A and Section B workflows, case/scenario-based questions, answer review/explanations, mock practice, flags, progress/statistics, written response practice/marking workflow, downloadable/printable reports, a doubt-submission flow, and theme handling.

### Embedded learning data

The JSON data block parses successfully and currently contains:

- 314 Section A question records.
- 63 scenario/case records.
- 77 Section B records.
- Section A question types include single-answer, matrix, multiple-response, single-table, columns and numeric formats.
- Question records include question number, scenario reference, marks, stem, type, answer and explanation; 260 of 314 records contain an `options` field, consistent with non-option question types also being present.

The two historical update reports in the archive describe earlier totals (275 and 314 questions / 67 Section B records). Those reports are stale relative to the current embedded dataset: current parsed totals are 314 / 77. Update the reports as part of documentation cleanup; do not assume the old reports describe the latest state.

### Authentication and persistence

The student page contains Firebase configuration and Google sign-in integration, a `REQUIRE_LOGIN` flag, Firestore sync code and local state persistence. Local storage is used for immediate/local state and should be treated as a cache, not proof of cross-device persistence. The setup guide says cloud account sync must be configured and tested before it is considered live. No real end-to-end Firebase test was possible in this offline source audit.

### Administrator application

The admin page has a Google sign-in gate and a client-side email allowlist. Its code reads student records and attempt/grade data and provides student/attempt administration workflows. The client-side allowlist is only a user-interface gate; Firestore rules must independently enforce every admin read/write.

## 4. Source-level checks

- Embedded question JSON: **PASS** (valid JSON).
- Student application executable inline JavaScript: **PASS** (2 executable blocks checked with `node --check`; JSON data block excluded).
- Administrator executable inline JavaScript: **PASS** (1 block checked with `node --check`).
- PDF files: page counts read successfully for the inventory above.
- ZIP integrity: archive extraction succeeded.
- Browser, Firebase, email delivery, cross-device sync and production build: **NOT TESTED**.

## 5. High-priority findings and risks

### P0 — Firestore security rules are not supplied as a complete deployable ruleset

The archive contains a progress-document rules example and a separate admin-only planner configuration snippet, but not the complete rules required by the admin page. The admin page queries the `users`, `attempts` and `gradings` collections and performs sensitive student-management operations. Before deployment, create and test a complete least-privilege ruleset that allows each student to access only their own records and grants admin operations only to a trusted backend-verified admin identity/claim or an equivalent securely enforced policy. Never rely on the JavaScript email allowlist as authorization. Review the admin email list and hardcoded addresses before public release.

### P0 — Admin privilege model requires backend verification

The `ADMIN_EMAILS` list appears in frontend code. This is not itself a secret, but it is not a security boundary. The exact same role decision must be enforced by Firestore rules or trusted server-side code. Validate that ordinary students cannot enumerate users, read other students' attempts, change roles, or delete records.

### P1 — Large monolithic HTML and embedded dataset

The student page combines roughly 2.24 MB of markup/styles/scripts/data in one file. This increases maintenance risk, makes focused testing difficult, and complicates content updates and SEO expansion. Refactor in stages into data modules, reusable UI components and service modules while preserving existing IDs/data semantics.

### P1 — Single-paper scope vs requested product scope

The supplied app is AA-focused. The master prompt asks for a multi-paper platform and a large public SEO/content architecture. Do not create empty subject pages or imply other paper banks exist. Treat AA as the first complete paper, then add other papers only with verified syllabus mapping and original/licensed content.

### P1 — Browser storage and cloud sync need reconciliation

The app writes local state to `localStorage` and separately dispatches state-save events for cloud synchronization. Test race conditions, account switching, sign-out, offline edits, conflict resolution, refresh recovery and cross-device restoration. Ensure one student's cached state cannot leak into another account on a shared browser.

### P1 — Documentation mismatch

`SECTION_A_MORE_REPORT.txt` and `SECTION_A_UPDATE_REPORT.txt` contain earlier totals and claims. Reconcile these documents against the current dataset. `FIREBASE_SETUP_GUIDE.txt` describes manual setup and says cloud sync is not active until configured and tested; verify whether the embedded Firebase project/config corresponds to an active, client-owned project before assuming service availability.

### P2 — External reference access unavailable during this audit

The supplied live Netlify URL and Instagram Reel could not be retrieved from this execution environment (network/DNS access failed; the web retrieval attempt also returned inaccessible). Their visual/functional details have therefore not been inferred. A browser recording or screenshots, or restored network access, will be needed for a faithful reference comparison.

### P2 — SEO is not yet an architecture for 50+ public pages

The archive contains two HTML application entry points rather than a multi-route content site. Audit and implement canonical URLs, metadata, sitemap, robots rules, SSR/static rendering and structured data only after selecting an architecture compatible with the existing hosting/backend. Student-only/private routes should not be indexed.

## 6. Preservation plan

1. Keep the supplied ZIP as the immutable baseline.
2. Preserve `index.html`, `admin.html`, all question/scenario/Section B records and every supplied resource.
3. Add automated snapshots/count checks for the embedded data before refactoring.
4. Extract data and pure logic first; keep existing user workflows operational.
5. Introduce a tested backend authorization model before expanding admin capabilities.
6. Migrate only authorized educational materials; the included BPP Exam Kit is copyrighted material and must not be copied into a public question bank without appropriate rights.

## 7. Recommended next implementation phases

### Phase 1A — Security and regression baseline (next)

- Obtain/confirm the actual deployed Firestore rules and Firebase project ownership.
- Write least-privilege rules tests for student isolation and admin-only operations.
- Add repeatable JSON/data validation and JavaScript regression tests.
- Test account switching and cross-device sync with two test accounts.

### Phase 1B — Safe maintainability refactor

- Extract question/scenario/Section B JSON into versioned data files without changing records.
- Separate Firebase/auth, persistence, practice engine, planner, rendering and admin services.
- Add a package/build/test setup only after confirming the target hosting environment.

### Phase 2 — Product foundation

- Establish public content routes and a shared design system.
- Keep AA as the initial fully supported paper.
- Add content management and import validation.
- Add SEO pages only where unique, reviewed content exists.

### Phase 3 — Multi-paper expansion

- Add paper-specific syllabuses and original/licensed question banks.
- Build analytics and study recommendations from genuine student activity.
- Add tested admin workflows, deployment automation and monitoring.

## 8. External configuration / decisions required

- Confirm the Firebase project is owned/controlled by the project owner and identify the production Firestore rules currently deployed. Do not send service-account private keys.
- Confirm whether Google sign-in is enabled and which domains are authorized.
- Confirm whether EmailJS is intended to be enabled; the supplied config has empty service/template/public-key fields and currently documents a mail-app fallback.
- Confirm target hosting (current Netlify or another platform) before choosing a framework migration.
- Confirm the authoritative admin accounts and whether backend custom claims are available.
- Confirm rights/licences for any commercial PDFs or question materials before public distribution.

## 9. Audit conclusion

The existing AA platform contains meaningful working product logic and substantial educational data. The safest route is a staged modernization, not a rewrite. The most urgent unresolved issue is the missing complete backend security ruleset for the operations exposed by the admin application. Browser-based functional tests and Firebase verification remain outstanding.

## Phase 3–5 implementation update (14 November 2026)

The Phase 2 package was used as the base. The current application and its original question bank were retained. Added a Node.js built-in regression suite (`tests/`), syntax-check runner, package scripts, and `docs/ARCHITECTURE.md`. The test suite currently passes 9 checks and validates the six Section A answer formats, Section B tutor-marking records, scenario references, core practice entry points, timer timestamp strategy, design accessibility hooks and Firestore rule structure.

Added a data-backed seven-day learning pulse to the Section A home screen, plus design-system CSS tokens, focus-visible states, responsive refinements, reduced-motion handling and subtle card/navigation styling. No sample statistics are used in the new dashboard panel.

This is still an incremental foundation, not completion of the 50+ page multi-paper platform. Browser-driven interaction testing and Firebase Emulator security testing remain release gates. The monolithic `index.html` has intentionally not been split yet; the architecture document defines the safer staged extraction plan.
