from __future__ import annotations

import argparse
import re
from pathlib import Path


DEFAULT_SOURCE_DIR = Path(__file__).resolve().parent.parent / "outputs" / "other"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize RAG text outputs into title-plus-paragraph plain text.")
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE_DIR), help="Directory containing .txt files to normalize.")
    parser.add_argument("--dry-run", action="store_true", help="Show which files would change without writing them.")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit on the number of files to process.")
    return parser.parse_args()


def normalize_title(raw_title: str) -> str:
    return re.sub(r"\s+", "", raw_title).replace("&", "＆")


def strip_leading_title(text: str, title: str) -> str:
    stripped = text.lstrip(" \t\r\n\u3000")
    candidates = [title]
    if title.endswith("？"):
        candidates.append(title[:-1])
    if title.endswith("！"):
        candidates.append(title[:-1])

    for candidate in candidates:
        if candidate and stripped.startswith(candidate):
            remainder = stripped[len(candidate) :]
            return remainder.lstrip(" \t\r\n\u3000：:。．，,、!?？！")
    return stripped


def is_list_item(line: str) -> bool:
    return bool(
        re.match(
            r"^(?:[◆‧•●○▪►]+|(?:[（(]?[0-9]+[)）.、．])|(?:[一二三四五六七八九十]+[、.．]))\s*",
            line,
        )
    )


def strip_list_marker(line: str) -> str:
    return re.sub(
        r"^(?:[◆‧•●○▪►]+|(?:[（(]?[0-9]+[)）.、．])|(?:[一二三四五六七八九十]+[、.．]))\s*",
        "",
        line,
    ).strip()


def looks_like_heading(line: str) -> bool:
    if not line or len(line) > 32:
        return False
    if line.endswith(("：", ":")):
        return True
    if re.search(r"[。！？!?；;]", line):
        return False
    if re.fullmatch(r"[A-Za-z0-9\s\-–—&/（）()【】《》「」『』：:]+", line):
        return False
    return True


def split_long_line(line: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"(?<=[。！？!?；;])\s*", line) if part.strip()]
    if len(parts) <= 1:
        return [line.strip()]

    grouped: list[str] = []
    buffer = ""
    target = 180
    for part in parts:
        if not buffer:
            buffer = part
            continue
        candidate = f"{buffer} {part}"
        if len(candidate) <= target:
            buffer = candidate
            continue
        grouped.append(buffer.strip())
        buffer = part
    if buffer:
        grouped.append(buffer.strip())
    return grouped


def compact_text(text: str) -> str:
    return re.sub(r"[\s\-‐‑‒–—。！？!?；;：:,，、()（）\[\]【】《》「」『』\"'`~·&/]+", "", text)


def normalize_body(text: str, title: str) -> str:
    text = text.replace("\ufeff", "").replace("\x00", "")
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\r\n?", "\n", text).strip()
    if not text:
        return ""

    raw_lines = [line.strip() for line in text.split("\n")]
    if len([line for line in raw_lines if line]) <= 3 and "\n\n" not in text and len(text) > 250:
        raw_lines = split_long_line(text.replace("\n", " "))

    lines: list[str] = []
    for raw_line in raw_lines:
        if not raw_line:
            lines.append("")
            continue
        line = re.sub(r"^[\-‐‑‒–—]+\s*", "", raw_line).strip()
        if not line:
            continue
        if is_list_item(line):
            line = strip_list_marker(line)
        lines.append(line)

    paragraphs: list[str] = []
    current: list[str] = []

    def flush() -> None:
        nonlocal current
        if current:
            paragraphs.append(" ".join(part.strip() for part in current if part.strip()).strip())
            current = []

    for line in lines:
        if not line:
            flush()
            continue

        if looks_like_heading(line):
            flush()
            paragraphs.append(line)
            continue

        if re.match(r"^[0-9一二三四五六七八九十]+[、.．)]?\s*", line) and len(line) <= 20:
            flush()
            paragraphs.append(line)
            continue

        if current and re.search(r"[。！？!?；;：:]$", current[-1]):
            flush()

        if not current:
            current.append(line)
            continue

        if len(line) <= 18 and not re.search(r"[。！？!?；;：:]", line):
            flush()
            paragraphs.append(line)
            continue

        current.append(line)

    flush()

    cleaned_paragraphs: list[str] = []
    for paragraph in paragraphs:
        paragraph = re.sub(r"\s+", " ", paragraph).strip()
        if paragraph:
            cleaned_paragraphs.append(paragraph)

    title_compact = compact_text(title)
    if cleaned_paragraphs and compact_text(cleaned_paragraphs[0]) == title_compact:
        cleaned_paragraphs = cleaned_paragraphs[1:]

    return "\n\n".join(cleaned_paragraphs)


def normalize_file(path: Path) -> tuple[bool, str]:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    normalized_raw = raw.replace("\r\n", "\n").replace("\r", "\n")
    title = normalize_title(path.stem)
    body = strip_leading_title(normalized_raw, title)
    normalized_body = normalize_body(body, title)

    if normalized_body:
        normalized = f"{title}\n\n{normalized_body}\n"
    else:
        normalized = f"{title}\n"

    changed = normalized != normalized_raw
    return changed, normalized


def main() -> int:
    args = parse_args()
    source_dir = Path(args.source_dir)
    files = sorted(source_dir.rglob("*.txt"))
    if args.limit and args.limit > 0:
        files = files[: args.limit]

    changed_count = 0
    for path in files:
        changed, normalized = normalize_file(path)
        if not changed:
            continue
        changed_count += 1
        if args.dry_run:
            print(f"WOULD UPDATE {path}")
            continue
        path.write_text(normalized, encoding="utf-8", newline="\n")
        print(f"UPDATED {path}")

    print(f"FILES SCANNED: {len(files)}")
    print(f"FILES CHANGED: {changed_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
