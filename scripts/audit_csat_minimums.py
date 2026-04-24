from __future__ import annotations

import json
import re
from pathlib import Path


BASE = Path("/Users/cheoljoopark/Desktop/product-v1/edu manage system")
DATA_PATH = BASE / "data" / "derived" / "university-info-119" / "universities.json"
OUT_PATH = BASE / "data" / "derived" / "university-info-119" / "csat-minimum-audit.md"

AMBIGUOUS_VALUES = {
    "적용",
    "있음",
    "적용 가능",
    "일부 모집단위 적용",
    "의·약 계열 일부 적용",
    "의/약 일부 적용",
    "의/치/약 일부 적용",
    "의/치/약/간 일부 적용",
    "의/치/약/수 일부 적용",
    "의예 등 일부 모집단위 적용",
    "치의예 계열 기준 적용",
    "약학 일부 적용",
    "간호 일부 적용",
}


def is_ambiguous_csat(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return False
    if text in AMBIGUOUS_VALUES:
        return True
    if "확인 필요" in text:
        return True
    return bool(re.fullmatch(r".*일부 적용", text))


def main() -> None:
    dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    findings = []
    for university in dataset["universities"]:
        for admission in university.get("structured_admissions", []):
            csat = str(admission.get("csat_minimum", "")).strip()
            if is_ambiguous_csat(csat):
                findings.append((university["name"], admission, csat))

    lines = [
        "# 수능최저 구체성 점검 리포트",
        "",
        "수능최저가 적용된 것으로 보이지만 `무슨 과목 몇 개 합 얼마` 형태로 충분히 구체화되지 않은 전형 후보입니다.",
        "이 목록은 원문 표를 추가 확인해 보완해야 합니다.",
        "",
        f"- 후보 수: {len(findings)}개",
        "",
    ]

    for name, admission, csat in findings:
        lines.extend(
            [
                f"## {name} - {admission.get('track_name', '전형명 미표기')}",
                "",
                f"- 전형유형: {admission.get('admission_type', '')}",
                f"- 현재 수능최저: {csat}",
                f"- 모집인원: {admission.get('capacity', '')}",
                f"- 전형방법: {admission.get('method', '')}",
                "",
            ]
        )

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")
    print(f"findings {len(findings)}")
    for name, admission, csat in findings[:80]:
        print(f"{name}\t{admission.get('admission_type')}\t{admission.get('track_name')}\t{csat}")


if __name__ == "__main__":
    main()
