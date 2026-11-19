# Firebase security and deployment notes

## Current project integration
The existing application uses Firebase Authentication and Cloud Firestore. The inspected client code accesses these paths:

- `users/{uid}` — student profile and summary statistics
- `users/{uid}/aaStudyHubProgress/current` — synchronised AA practice state
- `users/{uid}/subjectPractice/FR` — F7 / Financial Reporting practice state
- `users/{uid}/subjectPractice/PM` — F5 / Performance Management practice state
- `attempts/{attemptId}` — individual practice attempts
- `gradings/{gradingId}` — tutor/admin marking records, queried by `uid`
- `pdfs/{pdfId}` — shared resource links
- `config/planner` — shared exam date/time
- `mocks/{mockId}` and `mocks/{mockId}/questions/{questionId}` — tutor-uploaded and published mock papers
- `mockAttempts/{attemptId}` and nested `answers` — student mock submissions and tutor-released marks
- `commonDoubts/{doubtId}` — cross-subject student discussion and tutor replies

## Administrator identities
The current frontend allow-list contains:
- `akshat.y.shah1725@gmail.com`
- `yateseducationaccaresource@gmail.com`

The Firestore rules require a verified Firebase email claim and one of these addresses. Keep the frontend and backend lists identical. For a larger deployment, migrate to custom claims assigned by a trusted server rather than relying on an email allow-list.

## New mock upload, grading and common doubt features
- Admin uploads a PDF from **Mock exams**. Selectable PDF text is extracted with PDF.js; image-only/scanned pages use browser OCR (Tesseract.js).
- The parser splits numbered questions and identifies simple A–D options. The result is saved as a draft; an administrator must inspect and correct the text and marks before publishing.
- Published mocks appear as a student invitation on the matching subject page. Student answers are saved under their own attempt and answer subcollection. The admin reviews each answer, assigns marks per question, and releases the total; only that student and admins can read the attempt.
- The **Common Doubts** board is shared by AA, F5 and F7. Signed-in students can post and read questions; admins can publish tutor replies visible to everyone.
- Publish both `firestore.rules` and `storage.rules`. Storage is used for original mock PDFs. The current upload limit is 20 MB per PDF.
- PDF extraction is a best-effort draft conversion, not a guaranteed exam-layout parser. The admin review step is mandatory. Encrypted, malformed, or very low-quality scanned PDFs may fail extraction.

## Critical deployment sequence
1. Export/back up current Firestore data and rules.
2. Enable Firebase Storage and review both `firestore.rules` and `storage.rules` with the project owner.
3. Test using Firebase Emulator Suite or a non-production Firebase project.
4. Verify a student cannot list all users, read another student's progress/attempts, create grading records, modify the shared planner, or write protected user fields.
5. Verify an administrator can manage students, attempts, grading records, PDFs and planner configuration.
6. Publish the Firestore rules in Firestore Database → Rules and the Storage rules in Storage → Rules only after those tests pass.

## Owner deployment steps for the new workflows
1. In Firebase Console, enable the Storage bucket for this project.
2. Publish `firestore.rules` under Firestore Database → Rules.
3. Publish `storage.rules` under Storage → Rules.
4. Confirm the two admin email addresses are correct and Google Authentication is enabled.
5. Test upload, student submission, per-question marking, released results and cross-subject doubt replies with separate admin and student accounts.

## Known limitations / items requiring owner configuration
- FR/PM client sync and subject-scoped Firestore rules have been added, but no live Firebase project was connected during this development pass; deployment and cross-device sync remain unverified.
- Firebase Authentication provider settings and authorised domains must be checked in the owner's console.
- The email allow-list is suitable as an immediate restriction for the current small project, but custom claims backed by a trusted server are preferable for enterprise administration.
- Existing account progress uses browser local storage as a local cache plus Firestore cloud sync. Local storage is not the permanent cross-device source of truth.
- No automated emulator security tests have been run in this environment.

## Pre-production acceptance checklist
- [ ] Student A can sign in and sync progress.
- [ ] Student A cannot read Student B's profile or progress.
- [ ] Student A cannot read Student B's attempts or grading.
- [ ] Student A cannot create/update/delete PDFs or planner configuration.
- [ ] Student A cannot grant themselves admin or unban themselves.
- [ ] Admin can view student list and attempts.
- [ ] Admin can publish grades and manage PDFs/planner.
- [ ] Admin can upload a text/scanned mock PDF, inspect extracted questions, and publish a draft.
- [ ] Students receive the mock invitation, submit answers, and only their own released marks are visible.
- [ ] Common doubts are visible across all three subjects and tutor replies update for students.
- [ ] Sign-out clears the local account state as intended.
- [ ] Same student account restores AA, FR and PM progress on a second device.
