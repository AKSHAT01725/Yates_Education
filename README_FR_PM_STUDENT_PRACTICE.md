# Yates Education — AA + FR + PM practice project

## Student access

- Open `index.html` for the existing Audit & Assurance (AA) student system.
- From the AA home page, choose **F5 & F7 Practice** to open `fr-pm-practice.html`.
- F7 is Financial Reporting (FR); F5 is Performance Management (PM).

## Three-subject student features

- AA opens the original AA practice experience; F5 and F7 use the additional practice module.
- Modern animated visual design, responsive layout, hover/selection states and reduced-motion support.

## FR/PM student features
- Select a supplied mock/progress/consolidation paper.
- Navigate question by question across the available sections.
- Attempt objective questions and see an automatic result when an answer key is available.
- Enter written/numeric responses and reveal the supplied marking-guide text after saving.
- Bookmark questions, retry a question, review a paper and use the timed mock option.
- Keep FR and PM progress separate from each other and from AA.
- Sign in with Google to use the added subject-specific Firestore progress paths (subject to deployment of the updated rules).

## Content coverage

- FR/F7: 96 questions transcribed from three supplied papers, plus 10 original supplementary practice questions; 106 total. 94 supplied-paper records have corresponding answer text.
- PM/F5: 126 questions transcribed from four supplied papers, plus 10 original supplementary practice questions; 136 total. 94 supplied-paper records have corresponding answer text.
- PM Mock D has no supplied matching answer PDF. Two FR Mock D records have no extracted answer text.
- AA: 314 existing built-in objective questions, plus 10 original supplementary questions (324 objective questions total); the existing Section B bank remains available.
- The 20 supplementary FR/PM questions and 10 AA questions are original Yates Education practice items, not official ACCA/Kaplan past-paper questions. They are clearly labelled and require academic review.
- Supplied-paper FR/PM records remain marked for academic review and are not published as verified content.

## Local run

Run a static HTTP server from this folder:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000/index.html` or `http://localhost:8000/fr-pm-practice.html`.

## Validation

```bash
python tools/validate_banks.py
npm run test:all
```

Both commands pass in the packaged development environment. Firebase live sync, emulator rules tests, browser-driven UI testing and academic verification remain pre-release tasks. See `DEVELOPMENT_STATUS.md` and `docs/imports/FR_PM_INTEGRATION.md`.

## Admin mock upload and student common doubts
Open `admin.html` and choose **Mock exams** to upload a PDF. PDF.js extracts selectable text; scanned pages use Tesseract OCR. The automatic question split is a draft: edit and verify all prompts, options and maximum marks before saving and publishing. Once published, students in the selected subject see a mock invitation when they open the website. Submissions are visible in the admin mock list; award marks question by question and release them to the individual student's account.

The **Common Doubts** floating action is available on all three subject pages. Students can post and read the shared discussion; administrator replies appear live for all students. Publish both `firestore.rules` and `storage.rules` before using these features.
