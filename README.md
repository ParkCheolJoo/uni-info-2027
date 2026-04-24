# 2027 University Information Web Workspace

이 작업 폴더는 세 가지 층으로 구분합니다.

- `index.html`
  - 현재 브라우저에서 여는 진입점
- `web/`
  - 화면 코드
  - 현재는 `app.js`만 분리
- `data/source/`
  - PDF에서 직접 뽑은 원문 추출물
  - 목차, 페이지 원문, 섹션별 Markdown 보관
- `data/derived/`
  - 웹 검색용으로 다시 만든 파생 데이터
  - 대학 검색 데이터와 브라우저 로딩용 JS 보관
- `scripts/`
  - 추출/변환 스크립트

현재 작업 원칙:

- 원문을 건드리는 파일은 `data/source/` 아래에만 둔다.
- 검색이나 화면 렌더링을 위한 가공 파일은 `data/derived/` 아래에만 둔다.
- 브라우저에서 여는 파일은 루트 `index.html`과 `web/` 아래로 제한한다.

재생성 명령:

```bash
PYTHONPATH=/tmp/pdfextract python3 scripts/extract_university_pdf.py
python3 scripts/build_university_profiles.py
```
