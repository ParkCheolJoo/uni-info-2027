from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path("/Users/cheoljoopark/Desktop/product-v1/edu manage system")
DERIVED_DIR = BASE / "data" / "derived" / "university-info-119"
DATA_PATH = DERIVED_DIR / "universities.json"
EVIDENCE_PATH = DERIVED_DIR / "evidence.jsonl"
OUT_PATH = DERIVED_DIR / "sparse-admissions-audit.md"

IMPORTANT_SECTION_IDS = {
    "regular-01",
    "regular-02",
    "essay",
    "suneung",
    "regional",
    "medical-overview",
    "medical-features",
    "arts-sports",
    "major-free-choice",
    "low-income",
    "rural",
    "vocational",
}

TABLE_KEYWORDS = {
    "모집인원",
    "전형방법",
    "수능최저",
    "교과",
    "종합",
    "논술",
    "정시",
    "면접",
    "서류",
    "지역인재",
}

MANUALLY_VERIFIED_SPARSE_UNIVERSITIES = {
    # These were rechecked against the source tables; the extra hits are broad mentions
    # or aggregate/analysis rows rather than additional structured admissions.
    "추계예술대",
    "한국체육대",
    "서울한영대",
    "서울대",
    "고려대(세종)",
    "한양대(ERICA)",
}


def load_evidence() -> dict[str, list[dict]]:
    evidence_by_name: dict[str, list[dict]] = defaultdict(list)
    with EVIDENCE_PATH.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            record = json.loads(line)
            evidence_by_name[record["university_name"]].append(record)
    return evidence_by_name


def score_candidate(university: dict, evidence: list[dict]) -> tuple[int, list[str]]:
    structured_count = len(university.get("structured_admissions", []))
    evidence_count = len(evidence)
    important = [item for item in evidence if item.get("section_id") in IMPORTANT_SECTION_IDS]
    keyword_hits = [
        item
        for item in important
        if set(item.get("keywords", [])) & TABLE_KEYWORDS
        or any(keyword in item.get("snippet", "") for keyword in TABLE_KEYWORDS)
    ]
    section_count = len({item.get("section_id") for item in important})

    score = 0
    reasons = []
    if structured_count == 0 and evidence_count >= 3:
        score += 5
        reasons.append("구조화 전형 없음")
    if structured_count <= 1 and evidence_count >= 8:
        score += 4
        reasons.append("근거 수 대비 구조화 전형 1개 이하")
    if structured_count <= 2 and evidence_count >= 20:
        score += 3
        reasons.append("근거 수 대비 구조화 전형 2개 이하")
    if structured_count <= 2 and len(keyword_hits) >= 4:
        score += 3
        reasons.append("전형 관련 키워드 근거 다수")
    if structured_count <= 2 and section_count >= 3:
        score += 2
        reasons.append("여러 주요 섹션에 등장")
    return score, reasons


def main() -> None:
    dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    evidence_by_name = load_evidence()
    candidates = []

    for university in dataset["universities"]:
        if university["name"] in MANUALLY_VERIFIED_SPARSE_UNIVERSITIES:
            continue
        evidence = evidence_by_name.get(university["name"], [])
        score, reasons = score_candidate(university, evidence)
        if score <= 0:
            continue
        important = [item for item in evidence if item.get("section_id") in IMPORTANT_SECTION_IDS]
        section_counts = Counter(item.get("section_title", item.get("section_id", "")) for item in important)
        candidates.append(
            {
                "score": score,
                "name": university["name"],
                "region": university.get("region", ""),
                "structured_count": len(university.get("structured_admissions", [])),
                "evidence_count": len(evidence),
                "reasons": reasons,
                "sections": section_counts,
                "snippets": important[:4],
            }
        )

    candidates.sort(key=lambda item: (-item["score"], -item["evidence_count"], item["name"]))

    lines = [
        "# 구조화 전형 밀도 점검 리포트",
        "",
        "동신대(나주)처럼 원문 근거는 여러 곳에 있는데 현재 구조화 전형 수가 적은 대학 후보입니다.",
        "점수가 높을수록 누락 가능성이 큽니다. 자동 점검이므로 실제 수정 전에는 원문 표를 확인해야 합니다.",
        "",
        f"- 후보 수: {len(candidates)}개",
        "",
    ]

    for item in candidates:
        sections = ", ".join(f"{name} {count}" for name, count in item["sections"].most_common(5))
        lines.extend(
            [
                f"## {item['name']} ({item['region']})",
                "",
                f"- 점수: {item['score']}",
                f"- 현재 구조화 전형 수: {item['structured_count']}",
                f"- 원문 근거 수: {item['evidence_count']}",
                f"- 의심 사유: {', '.join(item['reasons'])}",
                f"- 주요 섹션: {sections or '없음'}",
                "",
            ]
        )
        for snippet in item["snippets"]:
            section = snippet.get("section_title", "")
            page = snippet.get("page", "")
            text = snippet.get("snippet", "")
            lines.extend([f"> {section} · PDF {page}: {text}", ""])

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")
    print(f"candidates {len(candidates)}")
    for item in candidates[:30]:
        print(
            f"{item['score']}\t{item['evidence_count']}\t{item['structured_count']}\t"
            f"{item['name']}\t{','.join(item['reasons'])}"
        )


if __name__ == "__main__":
    main()
