# Regression checks

Run with Node.js 18 or newer:

```sh
npm run test:all
```

The current suite checks source syntax, embedded AA dataset integrity, core practice-engine entry points, absolute-timestamp mock timing, the real-data weekly dashboard, responsive/reduced-motion design hooks, and the presence of Firestore ownership/admin policy functions.

These are source-level regression checks, not browser interaction tests and not Firebase security-emulator tests. Before release, add Playwright coverage against a staging build and Firebase Emulator Suite tests against the deployed ruleset.
