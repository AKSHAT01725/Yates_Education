#!/usr/bin/env python3
"""
OCR-first BPP Exam Kit ingestion for Yates Education.
Creates a page-preserving OCR archive and an administrator review queue.
It intentionally does NOT publish questions or guess answers/marks.
Requires: PyMuPDF (`pip install pymupdf`) and Tesseract OCR on PATH.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path
import fitz

QUESTION_RE = re.compile(
    r"(?im)^\s*(?:question|q(?:uestion)?\.?)\s*#?\s*(\d{1,4}[A-Z]?)\b"
)
ANSWER_RE = re.compile(r"(?im)^\s*(?:answer|answers)\s*(?:to\s*)?(?:question\s*)?#?\s*(\d{1,4}[A-Z]?)\b")

def ocr_page(page, dpi: int, lang: str, psm: int) -> str:
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
    proc = subprocess.run(
        ["tesseract", "stdin", "stdout", "-l", lang, "--psm", str(psm)],
        input=pix.tobytes("png"), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    return proc.stdout.decode("utf-8", "replace").replace("\x0c", "").strip()

def page_role(text: str) -> str:
    t = text.lower()
    if "answers" in t and ("question" in t or "mock exam" in t): return "answer_or_index"
    if "question index" in t or "contents" in t[:800]: return "front_matter"
    if re.search(r"\b(mock exam|practice exam)\b", t): return "mock_exam"
    return "question_or_answer"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--subject", choices=["FR","PM"], required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dpi", type=int, default=180)
    ap.add_argument("--lang", default="eng")
    ap.add_argument("--psm", type=int, default=3)
    ap.add_argument("--start-page", type=int, default=1)
    ap.add_argument("--end-page", type=int)
    ap.add_argument("--skip-existing", action="store_true")
    args = ap.parse_args()

    if not args.pdf.is_file(): ap.error(f"PDF not found: {args.pdf}")
    if args.dpi < 100: ap.error("Use at least 100 DPI for review-quality OCR.")
    args.out.mkdir(parents=True, exist_ok=True)
    pages_dir = args.out / "pages"
    pages_dir.mkdir(exist_ok=True)
    doc = fitz.open(args.pdf)
    end = min(args.end_page or len(doc), len(doc))
    start = max(1, args.start_page)
    if start > end: ap.error("start-page must be <= end-page")

    page_records = []
    for pno in range(start, end + 1):
        target = pages_dir / f"page-{pno:04d}.txt"
        if args.skip_existing and target.exists():
            text = target.read_text(encoding="utf-8")
        else:
            text = ocr_page(doc[pno-1], args.dpi, args.lang, args.psm)
            target.write_text(text, encoding="utf-8")
        page_records.append({
            "page": pno, "roleHint": page_role(text), "ocrText": text,
            "ocrStatus": "needs_visual_verification" if text else "empty_or_failed"
        })
        print(f"OCR {pno}/{end}", file=sys.stderr)

    # Preserve all OCR by page. Candidate segments are only review leads, not final questions.
    candidates = []
    active = None
    for rec in page_records:
        text = rec["ocrText"]
        hits = list(QUESTION_RE.finditer(text))
        # Avoid interpreting answer-key headings as question stems.
        if rec["roleHint"] == "answer_or_index" and ANSWER_RE.search(text):
            hits = []
        if hits:
            for idx, hit in enumerate(hits):
                if active:
                    candidates.append(active)
                chunk = text[hit.start(): hits[idx+1].start() if idx+1 < len(hits) else len(text)]
                active = {
                    "candidateId": f"{args.subject}-OCR-{len(candidates)+1:05d}",
                    "subject": args.subject,
                    "detectedQuestionNumber": hit.group(1),
                    "questionPages": [rec["page"]],
                    "rawOCR": chunk,
                    "verificationStatus": "needs_review",
                    "published": False
                }
        elif active and rec["roleHint"] == "question_or_answer":
            active["rawOCR"] += "\n\n" + text
            active["questionPages"].append(rec["page"])
    if active: candidates.append(active)

    bundle = {
        "schemaVersion": 1, "subject": args.subject,
        "sourcePdf": args.pdf.name, "totalSourcePages": len(doc),
        "processedPageRange": [start, end], "processedPageCount": len(page_records),
        "candidateCount": len(candidates),
        "warning": "OCR candidates are not verified questions. Confirm question boundaries, scenarios, exhibits, marks, answers and workings against original PDF pages before conversion or publication.",
        "pages": page_records, "candidates": candidates
    }
    (args.out / "ocr-review-queue.json").write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "subject": args.subject, "sourcePages": len(doc),
        "processedPages": len(page_records), "candidateSegments": len(candidates),
        "reviewQueue": str(args.out / "ocr-review-queue.json"),
        "publishedQuestions": 0
    }, indent=2))

if __name__ == "__main__":
    main()
