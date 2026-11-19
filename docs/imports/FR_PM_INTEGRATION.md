# FR & PM student-practice integration

## Student entry point

- `fr-pm-practice.html` is the FR/PM student practice interface.
- The existing AA renderer remains in `index.html`; the AA question data and AA storage key are not reused or renamed.
- The AA home screen now links to the FR/PM practice page.
- FR and PM have separate subject selection, paper selection, question navigation, objective answer checking where an answer key is available, written-response entry, answer reveal, retry, bookmarks, paper review and progress summaries.
- The same question experience is provided for Section A, Section B and Section C records. Section B scenario material is attached to each linked question so candidates can see the case context while answering.

## Imported content counts

| Subject | Papers | Questions | Supplied answer text |
|---|---:|---:|---:|
| FR / F7 | 3 | 96 | 94 records |
| PM / F5 | 4 | 126 | 94 records |
| **Total** | **7** | **222** | **188 records** |

Sources are the Kaplan PDFs supplied in `F7 Asset.zip` and `F5 Asset.zip`, represented by the page-preserving text files used to build the bank. PM Mock D has no matching answer PDF in the supplied asset set. Two FR Mock D records have no extracted matching answer text. These gaps are explicitly retained; no answer is invented.

## Data and review status

- `data/question-banks/fr.json` and `pm.json` contain question-level records, options where extractable, linked scenario context, source paper/page references, answer text where supplied, and a review status.
- Every imported question remains `verification.status = needs_review` or `missing_answer`.
- Both banks remain `published: false` at the manifest level. The practice page labels the content as transcribed and not yet academically verified.
- The extraction script is `tools/build_fr_pm_banks.py`. It preserves the source question text and answer text; it does not independently certify the correctness of OCR/transcription or answer mapping.

## Progress and Firebase

- Browser progress is isolated by subject in `yates-subject-practice-v1`; it does not overwrite `yates-aa-ot-v1`.
- Optional Google sign-in synchronisation writes to `users/{uid}/subjectPractice/FR` and `users/{uid}/subjectPractice/PM`.
- Firestore rules restrict each student to their own subject progress documents and allow administrators access.
- Firebase sync code and rules are prepared, but live Firebase authentication, emulator tests, cross-device reconciliation and production rule deployment have not been performed in this development environment. Do not claim cloud sync is production-certified until those tests pass.

## Run locally

Serve the `AA_Exam_Practice` folder over HTTP (not `file://`) because the FR/PM page fetches the JSON banks:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/index.html` and choose **F5 & F7 Practice**, or open `http://localhost:8000/fr-pm-practice.html` directly.

## Verification before publishing

An administrator should compare each question and answer with its source PDF, especially tables, negative figures, formulas, option ordering, multi-select wording, scenario boundaries and written marking schemes. Change the verification status only after review. The bank is intentionally not marked published by this import.
