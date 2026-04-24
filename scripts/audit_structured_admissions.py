from __future__ import annotations

import json
import re
from pathlib import Path


BASE = Path("/Users/cheoljoopark/Desktop/product-v1/edu manage system")
DATA_PATH = BASE / "data" / "derived" / "university-info-119" / "universities.json"
SECTIONS_DIR = BASE / "data" / "source" / "university-info-119" / "sections"
OUT_PATH = BASE / "data" / "derived" / "university-info-119" / "admissions-audit.md"

SECTION_EXPECTATIONS = {
    "05-student-record-subject.md": ("학생부교과", "학생부교과전형"),
    "06-student-record-comprehensive.md": ("학생부종합", "학생부종합전형"),
    "08-suneung.md": ("정시", "수능위주전형"),
}

WEAK_CONTEXT_PATTERNS = (
    "전형방법",
    "모집",
    "모집인원",
    "수능최저",
    "교과",
    "서류",
    "면접",
    "수능",
)


def normalize(value: str) -> str:
    return re.sub(r"\s+", "", value or "")


def compact_to_original_index(text: str) -> tuple[str, list[int]]:
    compact = []
    index_map = []
    for index, char in enumerate(text):
        if not char.isspace():
            compact.append(char)
            index_map.append(index)
    return "".join(compact), index_map


def snippets_for_name(text: str, compact_text: str, index_map: list[int], name: str, limit: int = 2) -> list[str]:
    needle = normalize(name)
    snippets = []
    start = 0
    while len(snippets) < limit:
        found = compact_text.find(needle, start)
        if found < 0:
            break
        original_index = index_map[found]
        begin = max(0, original_index - 180)
        end = min(len(text), original_index + 420)
        snippet = re.sub(r"\s+", " ", text[begin:end]).strip()
        snippets.append(snippet)
        start = found + len(needle)
    return snippets


def has_strong_context(snippet: str) -> bool:
    return sum(pattern in snippet for pattern in WEAK_CONTEXT_PATTERNS) >= 2


def main() -> None:
    dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    universities = dataset["universities"]
    sections = {}
    for filename in SECTION_EXPECTATIONS:
        text = (SECTIONS_DIR / filename).read_text(encoding="utf-8")
        compact, index_map = compact_to_original_index(text)
        sections[filename] = (text, compact, index_map)

    findings = []
    for university in universities:
        name = university["name"]
        current_types = {entry.get("admission_type") for entry in university.get("structured_admissions", [])}
        for filename, (expected_type, section_title) in SECTION_EXPECTATIONS.items():
            if expected_type in current_types:
                continue
            text, compact, index_map = sections[filename]
            snippets = snippets_for_name(text, compact, index_map, name)
            strong_snippets = [snippet for snippet in snippets if has_strong_context(snippet)]
            if strong_snippets:
                findings.append(
                    {
                        "name": name,
                        "missing_type": expected_type,
                        "section": section_title,
                        "current_types": sorted(filter(None, current_types)) or ["없음"],
                        "snippets": strong_snippets,
                    }
                )

    lines = [
        "# 구조화 전형 누락 의심 리포트",
        "",
        "PDF 추출 섹션에는 대학명이 강한 전형 문맥과 함께 등장하지만, 현재 `structured_admissions`에는 해당 전형유형이 없는 후보입니다.",
        "자동 점검 결과이므로 최종 반영 전 원문 표 확인이 필요합니다.",
        "",
        f"- 전체 대학: {len(universities)}개",
        f"- 누락 의심 후보: {len(findings)}건",
        "",
    ]

    for finding in findings:
        lines.extend(
            [
                f"## {finding['name']} - {finding['missing_type']} 누락 의심",
                "",
                f"- 현재 구조화 전형유형: {', '.join(finding['current_types'])}",
                f"- 원문 발견 섹션: {finding['section']}",
                "",
            ]
        )
        for snippet in finding["snippets"]:
            lines.extend([f"> {snippet}", ""])

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")
    print(f"findings {len(findings)}")
    for finding in findings[:40]:
        print(f"{finding['name']}\t{finding['missing_type']}\tcurrent={','.join(finding['current_types'])}")


if __name__ == "__main__":
    main()
