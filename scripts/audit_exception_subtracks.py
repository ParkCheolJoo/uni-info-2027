from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path("/Users/cheoljoopark/Desktop/product-v1/edu manage system")
DATA_PATH = BASE / "data" / "derived" / "university-info-119" / "universities.json"
SECTIONS_DIR = BASE / "data" / "source" / "university-info-119" / "sections"
OUT_PATH = BASE / "data" / "derived" / "university-info-119" / "exception-subtracks-audit.md"

TARGET_SECTION_FILES = [
    "06-student-record-comprehensive.md",
    "22-arts-sports.md",
    "05-student-record-subject.md",
]

UNIVERSITY_LINE_RE = re.compile(r"^[가-힣A-Za-z0-9·&\-\(\)\s]+$")
EXCEPTION_LINE_RE = re.compile(r"^[※△]\s*\(?([^)]+?)\)?$")
INLINE_EXCEPTION_RE = re.compile(r"[△※]\(([^)]+)\)")
GENERIC_TOKENS = {
    "전 모집단위",
    "일부",
    "일반",
    "인문",
    "자연",
    "공학",
    "약",
    "의",
    "치",
    "한",
    "의예",
    "치의예",
    "한의예",
    "약학",
    "배수",
    "응시",
    "반영",
    "포함",
    "안함",
    "표기",
    "경우는",
    "학년",
    "학년별",
    "미반영",
    "미발표",
    "또는",
    "100’인",
    "‘전",
    "예체능계",
    "인문․예체능",
    "자연․공학",
    "국 포함",
    "수 포함",
    "영2",
    "간",
    "의",
    "약",
    "수",
}
GENERIC_SUBSTRINGS = (
    "대학",
    "배수",
    "직탐",
    "응시",
    "포함",
    "제2외",
    "한문",
    "가능",
    "제외",
    "자유전공",
    "열린전공",
    "첨단융합학부",
    "학부대학",
)
IGNORE_LINE_KEYWORDS = (
    "배수",
    "직탐 가능",
    "응시",
    "제2외",
    "한문",
    "국 포함",
    "수 포함",
    "영2",
)

MANUALLY_VERIFIED = {
    "서울대",
    "상명대",
    "서울교대",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", str(text or "")).lower()


def compact_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def extract_exception_tokens(line: str) -> list[str]:
    tokens: list[str] = []
    for match in INLINE_EXCEPTION_RE.finditer(line):
        raw = match.group(1)
        tokens.extend(split_exception_names(raw))

    match = EXCEPTION_LINE_RE.match(line)
    if match:
        tokens.extend(split_exception_names(match.group(1)))
    return [token for token in tokens if token]


def split_exception_names(raw: str) -> list[str]:
    cleaned = raw
    parts = re.split(r"[·,/]| 및 ", cleaned)
    results = []
    for part in parts:
        token = part.strip(" -–—()")
        token = re.sub(r"\s+", " ", token)
        if not token:
            continue
        if "(" in token or ")" in token:
            continue
        if any(char.isdigit() for char in token):
            continue
        if token in GENERIC_TOKENS:
            continue
        if any(fragment in token for fragment in GENERIC_SUBSTRINGS):
            continue
        if token.endswith("기준"):
            continue
        if len(token) <= 1:
            continue
        if len(token) >= 18:
            continue
        if any(word in token for word in ["배수", "반영", "응시", "학년", "모집단위", "전 모집단위"]):
            continue
        results.append(token)
    return results


def merged_exception_line(window: list[str], offset: int) -> str:
    line = window[offset]
    if offset + 1 >= len(window):
        return line

    next_line = window[offset + 1]
    if not line.startswith(("※", "△")):
        return line
    if next_line.startswith(("※", "△", "-", "×", "○")):
        return line
    if UNIVERSITY_LINE_RE.match(next_line) and "(" in next_line and ")" in next_line:
        return line
    if any(keyword in line for keyword in IGNORE_LINE_KEYWORDS):
        return line

    if line.endswith(("디", "문", "대", "계", "과", "부", ",", "(")) or line.count("(") > line.count(")"):
        return f"{line}{next_line}"
    return line


def collect_exception_mentions(university_name: str, base_name: str, base_name_counts: dict[str, int]) -> list[dict]:
    aliases = {university_name}
    if base_name_counts.get(base_name, 0) <= 1:
        aliases.add(base_name)
    findings: list[dict] = []
    for filename in TARGET_SECTION_FILES:
        path = SECTIONS_DIR / filename
        lines = compact_lines(path.read_text(encoding="utf-8"))
        for idx, line in enumerate(lines):
            if line not in aliases:
                continue
            window = lines[idx + 1 : idx + 18]
            for offset, candidate in enumerate(window, start=1):
                if offset > 1 and candidate in aliases:
                    break
                if candidate.startswith("## 원본 페이지"):
                    break
                if offset > 2 and UNIVERSITY_LINE_RE.match(candidate) and "(" in candidate and ")" in candidate:
                    break
                merged = merged_exception_line(window, offset - 1)
                if any(keyword in merged for keyword in IGNORE_LINE_KEYWORDS):
                    continue
                tokens = extract_exception_tokens(merged)
                if not tokens:
                    continue
                findings.append(
                    {
                        "source": filename,
                        "anchor": line,
                        "line": merged,
                        "tokens": tokens,
                        "context": " / ".join(window[max(0, offset - 2) : min(len(window), offset + 2)]),
                    }
                )
    return findings


def has_matching_subtrack(admissions: list[dict], token: str) -> bool:
    token_norm = normalize(token)
    for admission in admissions:
        track = normalize(admission.get("track_name", ""))
        notes = normalize(admission.get("notes", ""))
        csat = normalize(admission.get("csat_minimum", ""))
        if token_norm and (token_norm in track or token_norm in notes or token_norm in csat):
            return True
    return False


def main() -> None:
    dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    base_name_counts: dict[str, int] = defaultdict(int)
    for university in dataset["universities"]:
        base_name_counts[university.get("base_name", university["name"])] += 1
    candidates = []

    for university in dataset["universities"]:
        name = university["name"]
        if name in MANUALLY_VERIFIED:
            continue
        admissions = university.get("structured_admissions", [])
        if not admissions:
            continue

        mentions = collect_exception_mentions(name, university.get("base_name", name), base_name_counts)
        if not mentions:
            continue

        missing = []
        seen = set()
        for mention in mentions:
            for token in mention["tokens"]:
                key = (mention["source"], token)
                if key in seen:
                    continue
                seen.add(key)
                if has_matching_subtrack(admissions, token):
                    continue
                missing.append(
                    {
                        "token": token,
                        "source": mention["source"],
                        "line": mention["line"],
                        "context": mention["context"],
                    }
                )

        if missing:
            candidates.append(
                {
                    "name": name,
                    "region": university.get("region", ""),
                    "structured_tracks": [item.get("track_name", "") for item in admissions],
                    "missing": missing,
                }
            )

    candidates.sort(key=lambda item: (-len(item["missing"]), item["name"]))

    lines = [
        "# 예외 모집단위 분리 점검 리포트",
        "",
        "서울대처럼 원문에 `※`, `△`, 예외 모집단위가 보이는데 현재 구조화 데이터에 별도 전형으로 분리되지 않았을 가능성이 있는 대학 후보입니다.",
        "자동 점검이므로 실제 수정 전에는 원문 표를 다시 확인해야 합니다.",
        "",
        f"- 후보 수: {len(candidates)}개",
        "",
    ]

    for candidate in candidates:
        lines.extend(
            [
                f"## {candidate['name']} ({candidate['region']})",
                "",
                f"- 현재 전형명: {', '.join(candidate['structured_tracks'])}",
                "",
            ]
        )
        for item in candidate["missing"]:
            lines.extend(
                [
                    f"- 누락 의심 모집단위: `{item['token']}`",
                    f"  - 출처: `{item['source']}`",
                    f"  - 원문 줄: {item['line']}",
                    f"  - 문맥: {item['context']}",
                    "",
                ]
            )

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")
    print(f"candidates {len(candidates)}")
    for candidate in candidates[:50]:
        tokens = ",".join(sorted({item['token'] for item in candidate["missing"]}))
        print(f"{len(candidate['missing'])}\t{candidate['name']}\t{tokens}")


if __name__ == "__main__":
    main()
