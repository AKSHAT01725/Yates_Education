# Yates Education implementation update — 21 November 2026

## Added in this working package
- A responsive subject-selection portal at `subjects.html`, designed as a polished first-stop dashboard for AA, FR and PM.
- Dedicated subject cards, clear entry points, responsive layout, hover motion, reduced-motion support and a visual identity per paper.
- FR and PM bank counts are read from their actual JSON files at runtime rather than fabricated figures.
- Subject portal navigation added to AA and FR/PM practice pages, so students can move between paper experiences.
- Content verification notice shown on the portal: imported FR/PM records remain subject to academic review and answer-key availability is not overstated.

## Existing platform preserved
- AA original page and question data.
- Existing FR/PM practice interface and bank files.
- Admin mock PDF workflow, question review draft and publish controls.
- Student mock attempt, tutor marking/release, common-doubt board and Firebase rules/configuration notes.

## Validation
The existing test suite and question-bank validation were run against the source package before this portal addition and passed. Re-run tests after modifications and package validation. Browser-based testing and live Firebase verification are not performed by this package editing process.
