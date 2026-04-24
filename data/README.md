# Data Layout

`data/`는 역할별로 두 층으로 나눕니다.

- `source/`: PDF에서 직접 추출한 원문성 데이터
- `derived/`: `source/`를 다시 가공해 만든 검색/웹용 파생 데이터

현재 구조:

- `source/university-info-119/manifest.json`
- `source/university-info-119/toc.json`
- `source/university-info-119/pages/pages.jsonl`
- `source/university-info-119/sections/*.md`
- `source/university-info-119/sections/index.json`
- `derived/university-info-119/universities.json`
- `derived/university-info-119/universities.js`

재생성:

```bash
PYTHONPATH=/tmp/pdfextract python3 scripts/extract_university_pdf.py
python3 scripts/build_university_profiles.py
```
