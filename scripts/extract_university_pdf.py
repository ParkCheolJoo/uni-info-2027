from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path("/Users/cheoljoopark/Desktop/university information app/2027_University information 119.pdf")
OUTPUT_DIR = Path("/Users/cheoljoopark/Desktop/product-v1/edu manage system/data/source/university-info-119")
PRINTED_TO_PDF_OFFSET = 6


@dataclass(frozen=True)
class LeafSection:
    id: str
    slug: str
    title: str
    printed_start: int | None
    printed_end: int | None
    pdf_start: int | None = None
    pdf_end: int | None = None
    part: str = ""
    group: str = ""


LEAF_SECTIONS = [
    LeafSection(
        id="front-matter",
        slug="00-front-matter",
        title="발간사 · 일러두기 · 목차",
        printed_start=None,
        printed_end=None,
        pdf_start=3,
        pdf_end=8,
        part="front-matter",
        group="front-matter",
    ),
    LeafSection("major-01", "01-major-schedule", "대입전형 일정", 3, 3, part="2027학년도 대입 주요 사항", group="2027학년도 대입 주요 사항"),
    LeafSection("major-02", "02-major-plan-features", "대입전형 시행계획 주요특징", 4, 22, part="2027학년도 대입 주요 사항", group="2027학년도 대입 주요 사항"),
    LeafSection("major-03", "03-major-summary", "2027학년도 대입전형 특징 요약", 23, 25, part="2027학년도 대입 주요 사항", group="2027학년도 대입 주요 사항"),
    LeafSection("major-04", "04-major-changes", "전년대비 변경사항", 26, 86, part="2027학년도 대입 주요 사항", group="2027학년도 대입 주요 사항"),
    LeafSection("regular-01", "05-student-record-subject", "학생부교과전형", 87, 141, part="1부 수시모집", group="1부 수시모집"),
    LeafSection("regular-02", "06-student-record-comprehensive", "학생부종합전형", 142, 186, part="1부 수시모집", group="1부 수시모집"),
    LeafSection("regular-03", "07-essay", "논술전형", 187, 222, part="1부 수시모집", group="1부 수시모집"),
    LeafSection("regular-04", "08-suneung", "수능전형(예체능 제외)", 223, 260, part="2부 정시모집", group="2부 정시모집"),
    LeafSection("special-01", "09-opportunity-integrated", "기회균형 선발 대상자(통합)전형", 261, 270, part="특별전형", group="기회균형 특별전형"),
    LeafSection("special-02", "10-rural", "농어촌학생 특별전형", 271, 288, part="특별전형", group="기회균형 특별전형"),
    LeafSection("special-03", "11-low-income", "기초생활수급자·차상위계층·한부모가족지원대상자 특별전형", 289, 303, part="특별전형", group="기회균형 특별전형"),
    LeafSection("special-04", "12-vocational", "특성화고교졸업자 특별전형", 304, 312, part="특별전형", group="기회균형 특별전형"),
    LeafSection("special-05", "13-disability", "장애인 등 대상자 특별전형", 313, 319, part="특별전형", group="기회균형 특별전형"),
    LeafSection("special-06", "14-regional", "지역인재 특별전형", 320, 378, part="특별전형", group="지역인재 특별전형"),
    LeafSection("analysis-01", "15-medical-overview", "2027학년도 의치약한수계열 개요", 379, 383, part="계열별 전형 분석과 준비", group="의치약한수계열"),
    LeafSection("analysis-02", "16-medical-features", "2027학년도 의치약한수계열 특징", 384, 424, part="계열별 전형 분석과 준비", group="의치약한수계열"),
    LeafSection("analysis-03", "17-medical-analysis", "의학계열 2024~2026학년도 입학정보 분석 현황", 425, 468, part="계열별 전형 분석과 준비", group="의치약한수계열"),
    LeafSection("analysis-04", "18-education", "교육계열(초등교육)", 469, 478, part="계열별 전형 분석과 준비", group="교육계열"),
    LeafSection("analysis-05", "19-science-specialized", "이공계 특성화 대학", 479, 484, part="계열별 전형 분석과 준비", group="이공계 특성화 대학"),
    LeafSection("analysis-06", "20-major-free-choice", "전공자율선택제", 485, 557, part="계열별 전형 분석과 준비", group="전공자율선택제"),
    LeafSection("analysis-07", "21-contract-cutting-edge", "계약학과·첨단학과", 558, 574, part="계열별 전형 분석과 준비", group="계약학과·첨단학과"),
    LeafSection("analysis-08", "22-arts-sports", "예체능계열(실기·실적전형 제외)", 575, 630, part="계열별 전형 분석과 준비", group="예체능계열"),
    LeafSection("appendix-01", "23-education-statistics", "각종 교육통계 참고자료", 631, 633, part="부록", group="부록"),
    LeafSection("appendix-02", "24-career-centers", "전국 시·도 교육청 진로진학 센터 안내", 634, 634, part="부록", group="부록"),
    LeafSection("appendix-03", "25-university-directory", "전국 대학 일람", 635, 648, part="부록", group="부록"),
]


TOC = [
    {
        "id": "front-matter",
        "title": "발간사 · 일러두기 · 목차",
        "file": "sections/00-front-matter.md",
        "children": [],
    },
    {
        "id": "major",
        "title": "2027학년도 대입 주요 사항",
        "children": [
            {"id": "major-01", "title": "대입전형 일정", "file": "sections/01-major-schedule.md"},
            {"id": "major-02", "title": "대입전형 시행계획 주요특징", "file": "sections/02-major-plan-features.md"},
            {"id": "major-03", "title": "2027학년도 대입전형 특징 요약", "file": "sections/03-major-summary.md"},
            {"id": "major-04", "title": "전년대비 변경사항", "file": "sections/04-major-changes.md"},
        ],
    },
    {
        "id": "regular-early",
        "title": "1부 수시모집",
        "children": [
            {"id": "regular-01", "title": "학생부교과전형", "file": "sections/05-student-record-subject.md"},
            {"id": "regular-02", "title": "학생부종합전형", "file": "sections/06-student-record-comprehensive.md"},
            {"id": "regular-03", "title": "논술전형", "file": "sections/07-essay.md"},
        ],
    },
    {
        "id": "regular-late",
        "title": "2부 정시모집",
        "children": [
            {"id": "regular-04", "title": "수능전형(예체능 제외)", "file": "sections/08-suneung.md"},
        ],
    },
    {
        "id": "special",
        "title": "특별전형",
        "children": [
            {
                "id": "special-opportunity",
                "title": "기회균형 특별전형",
                "children": [
                    {"id": "special-01", "title": "기회균형 선발 대상자(통합)전형", "file": "sections/09-opportunity-integrated.md"},
                    {"id": "special-02", "title": "농어촌학생 특별전형", "file": "sections/10-rural.md"},
                    {"id": "special-03", "title": "기초생활수급자·차상위계층·한부모가족지원대상자 특별전형", "file": "sections/11-low-income.md"},
                    {"id": "special-04", "title": "특성화고교졸업자 특별전형", "file": "sections/12-vocational.md"},
                    {"id": "special-05", "title": "장애인 등 대상자 특별전형", "file": "sections/13-disability.md"},
                ],
            },
            {"id": "special-06", "title": "지역인재 특별전형", "file": "sections/14-regional.md"},
        ],
    },
    {
        "id": "analysis",
        "title": "계열별 전형 분석과 준비",
        "children": [
            {
                "id": "analysis-medical",
                "title": "의치약한수계열",
                "children": [
                    {"id": "analysis-01", "title": "2027학년도 의치약한수계열 개요", "file": "sections/15-medical-overview.md"},
                    {"id": "analysis-02", "title": "2027학년도 의치약한수계열 특징", "file": "sections/16-medical-features.md"},
                    {"id": "analysis-03", "title": "의학계열 2024~2026학년도 입학정보 분석 현황", "file": "sections/17-medical-analysis.md"},
                ],
            },
            {"id": "analysis-04", "title": "교육계열(초등교육)", "file": "sections/18-education.md"},
            {"id": "analysis-05", "title": "이공계 특성화 대학", "file": "sections/19-science-specialized.md"},
            {"id": "analysis-06", "title": "전공자율선택제", "file": "sections/20-major-free-choice.md"},
            {"id": "analysis-07", "title": "계약학과·첨단학과", "file": "sections/21-contract-cutting-edge.md"},
            {"id": "analysis-08", "title": "예체능계열(실기·실적전형 제외)", "file": "sections/22-arts-sports.md"},
        ],
    },
    {
        "id": "appendix",
        "title": "부록",
        "children": [
            {"id": "appendix-01", "title": "각종 교육통계 참고자료", "file": "sections/23-education-statistics.md"},
            {"id": "appendix-02", "title": "전국 시·도 교육청 진로진학 센터 안내", "file": "sections/24-career-centers.md"},
            {"id": "appendix-03", "title": "전국 대학 일람", "file": "sections/25-university-directory.md"},
        ],
    },
]


def printed_to_pdf_page(printed_page: int) -> int:
    return printed_page + PRINTED_TO_PDF_OFFSET


def clean_text(raw: str) -> str:
    text = raw.replace("\u00a0", " ").replace("\uf06e", "•").replace("\uf0b7", "•")
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped == "2027학년도 대입정보 119":
            continue
        if re.fullmatch(r"\d+", stripped):
            continue
        lines.append(stripped)
    text = "\n".join(lines).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def extract_pages(reader: PdfReader) -> list[dict]:
    pages = []
    for idx, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        cleaned = clean_text(raw)
        printed_page = idx - PRINTED_TO_PDF_OFFSET if idx > PRINTED_TO_PDF_OFFSET else None
        pages.append(
            {
                "pdf_page": idx,
                "printed_page": printed_page,
                "text": cleaned,
            }
        )
    return pages


def section_pages(section: LeafSection) -> tuple[int, int]:
    if section.pdf_start and section.pdf_end:
        return section.pdf_start, section.pdf_end
    if section.printed_start is None or section.printed_end is None:
        raise ValueError(f"Missing page range for {section.id}")
    return printed_to_pdf_page(section.printed_start), printed_to_pdf_page(section.printed_end)


def build_markdown(section: LeafSection, page_entries: list[dict]) -> str:
    pdf_start, pdf_end = section_pages(section)
    meta = {
        "id": section.id,
        "title": section.title,
        "part": section.part,
        "group": section.group,
        "source_pdf": str(PDF_PATH),
        "pdf_pages": [pdf_start, pdf_end],
        "printed_pages": [section.printed_start, section.printed_end],
    }
    lines = ["---", json.dumps(meta, ensure_ascii=False, indent=2), "---", "", f"# {section.title}", ""]
    if section.part:
        lines.append(f"- 분류: {section.part}")
    if section.group and section.group != section.part:
        lines.append(f"- 하위 그룹: {section.group}")
    lines.append(f"- PDF 페이지: {pdf_start}~{pdf_end}")
    if section.printed_start is not None and section.printed_end is not None:
        lines.append(f"- 책자 기준 페이지: {section.printed_start}~{section.printed_end}")
    lines.append("")
    for entry in page_entries:
        heading = f"## 원본 페이지 {entry['pdf_page']}"
        if entry["printed_page"] is not None:
            heading += f" (책자 {entry['printed_page']}쪽)"
        lines.extend([heading, "", entry["text"] or "[텍스트 추출 없음]", ""])
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "sections").mkdir(exist_ok=True)
    (OUTPUT_DIR / "pages").mkdir(exist_ok=True)

    reader = PdfReader(str(PDF_PATH))
    pages = extract_pages(reader)

    manifest = {
        "title": "2027학년도 대입정보 119",
        "source_pdf": str(PDF_PATH),
        "total_pdf_pages": len(reader.pages),
        "printed_to_pdf_offset": PRINTED_TO_PDF_OFFSET,
        "generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "section_count": len(LEAF_SECTIONS),
        "formats": ["markdown", "json", "jsonl"],
    }

    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUTPUT_DIR / "toc.json").write_text(json.dumps(TOC, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with (OUTPUT_DIR / "pages" / "pages.jsonl").open("w", encoding="utf-8") as fp:
        for page in pages:
            fp.write(json.dumps(page, ensure_ascii=False) + "\n")

    section_index = []
    for section in LEAF_SECTIONS:
        pdf_start, pdf_end = section_pages(section)
        page_entries = pages[pdf_start - 1 : pdf_end]
        markdown = build_markdown(section, page_entries)
        path = OUTPUT_DIR / "sections" / f"{section.slug}.md"
        path.write_text(markdown, encoding="utf-8")
        section_index.append(
            {
                "id": section.id,
                "title": section.title,
                "slug": section.slug,
                "path": str(path.relative_to(OUTPUT_DIR)),
                "part": section.part,
                "group": section.group,
                "pdf_pages": [pdf_start, pdf_end],
                "printed_pages": [section.printed_start, section.printed_end],
            }
        )

    (OUTPUT_DIR / "sections" / "index.json").write_text(
        json.dumps(section_index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
