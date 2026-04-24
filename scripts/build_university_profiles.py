from __future__ import annotations

import copy
import json
import re
from collections import defaultdict
from pathlib import Path


BASE = Path("/Users/cheoljoopark/Desktop/product-v1/edu manage system")
SOURCE_DIR = BASE / "data" / "source" / "university-info-119"
SECTIONS_DIR = SOURCE_DIR / "sections"
DERIVED_DIR = BASE / "data" / "derived" / "university-info-119"
OUT_JSON = DERIVED_DIR / "universities.json"
OUT_JS = DERIVED_DIR / "universities.js"
OUT_CATALOG = DERIVED_DIR / "catalog.json"
OUT_EVIDENCE = DERIVED_DIR / "evidence.jsonl"

ADMISSION_URL_OVERRIDES = {
    "서울대": "https://admission.snu.ac.kr/index.html",
}

MANUAL_DIRECTORY_ENTRIES = {
    "을지대(성남)": {
        "id": "을지대-성남",
        "name": "을지대(성남)",
        "base_name": "을지대",
        "campus": "성남",
        "normalized_name": "을지대(성남)",
        "region": "경기",
        "website": "https://www.eulji.ac.kr",
        "phone": "1899-0001, 031-740-7106~7,7277",
        "address": "경기도 성남시 수정구 산성대로 553",
        "directory_page": 644,
    },
    "한경국립대(안성)": {
        "id": "한경국립대-안성",
        "name": "한경국립대(안성)",
        "base_name": "한경국립대",
        "campus": "안성",
        "normalized_name": "한경국립대(안성)",
        "region": "경기",
        "website": "https://www.hknu.ac.kr",
        "phone": "031-670-5042~4",
        "address": "경기도 안성시 중앙로 327",
        "directory_page": 644,
    },
    "신한대(의정부)": {
        "id": "신한대-의정부",
        "name": "신한대(의정부)",
        "base_name": "신한대",
        "campus": "의정부",
        "normalized_name": "신한대(의정부)",
        "region": "경기",
        "website": "https://www.shinhan.ac.kr",
        "phone": "031-870-3211~7",
        "address": "경기도 의정부시 호암로 95",
        "directory_page": 643,
    },
    "신한대(동두천)": {
        "id": "신한대-동두천",
        "name": "신한대(동두천)",
        "base_name": "신한대",
        "campus": "동두천",
        "normalized_name": "신한대(동두천)",
        "region": "경기",
        "website": "https://www.shinhan.ac.kr",
        "phone": "",
        "address": "경기도 동두천시 벌마들로 40번길 30",
        "directory_page": 643,
    },
    "수원대(화성)": {
        "id": "수원대-화성",
        "name": "수원대(화성)",
        "base_name": "수원대",
        "campus": "화성",
        "normalized_name": "수원대(화성)",
        "region": "경기",
        "website": "https://www.suwon.ac.kr",
        "phone": "031-229-8420~2",
        "address": "경기도 화성시 봉담읍 와우안길 17",
        "directory_page": 643,
    },
    "국립한국교통대(충주)": {
        "id": "국립한국교통대-충주",
        "name": "국립한국교통대(충주)",
        "base_name": "국립한국교통대",
        "campus": "충주",
        "normalized_name": "국립한국교통대(충주)",
        "region": "충북",
        "website": "https://www.ut.ac.kr",
        "phone": "043-841-5114",
        "address": "충북 충주시 대학로 50",
        "directory_page": 644,
    },
    "전북대(전주)": {
        "id": "전북대-전주",
        "name": "전북대(전주)",
        "base_name": "전북대",
        "campus": "전주",
        "normalized_name": "전북대(전주)",
        "region": "전북",
        "website": "https://www.jbnu.ac.kr",
        "phone": "063-270-2500",
        "address": "전북 전주시 덕진구 백제대로 567",
        "directory_page": 644,
    },
    "전북대(특성화)": {
        "id": "전북대-특성화",
        "name": "전북대(특성화)",
        "base_name": "전북대",
        "campus": "특성화",
        "normalized_name": "전북대(특성화)",
        "region": "전북",
        "website": "https://www.jbnu.ac.kr",
        "phone": "063-270-2500",
        "address": "전북 익산시 고봉로 79",
        "directory_page": 644,
    },
    "경상국립대(진주)": {
        "id": "경상국립대-진주",
        "name": "경상국립대(진주)",
        "base_name": "경상국립대",
        "campus": "진주",
        "normalized_name": "경상국립대(진주)",
        "region": "경남",
        "website": "https://www.gnu.ac.kr",
        "phone": "055-772-1115~6",
        "address": "경남 진주시 진주대로 501",
        "directory_page": 643,
    },
    "경상국립대(칠암)": {
        "id": "경상국립대-칠암",
        "name": "경상국립대(칠암)",
        "base_name": "경상국립대",
        "campus": "칠암",
        "normalized_name": "경상국립대(칠암)",
        "region": "경남",
        "website": "https://www.gnu.ac.kr",
        "phone": "055-772-1115~6",
        "address": "경남 진주시 동진로 33",
        "directory_page": 643,
    },
    "국립강릉원주대(원주)": {
        "id": "국립강릉원주대-원주",
        "name": "국립강릉원주대(원주)",
        "base_name": "국립강릉원주대",
        "campus": "원주",
        "normalized_name": "국립강릉원주대(원주)",
        "region": "강원",
        "website": "https://www.gwnu.ac.kr",
        "phone": "033-640-2739, 2741",
        "address": "강원도 원주시 흥업면 남원로 150",
        "directory_page": 642,
    },
    "국립공주대(공주)": {
        "id": "국립공주대-공주",
        "name": "국립공주대(공주)",
        "base_name": "국립공주대",
        "campus": "공주",
        "normalized_name": "국립공주대(공주)",
        "region": "충남",
        "website": "https://www.kongju.ac.kr",
        "phone": "041-850-0111",
        "address": "충남 공주시 공주대학로 56",
        "directory_page": 643,
    },
    "국립공주대(예산)": {
        "id": "국립공주대-예산",
        "name": "국립공주대(예산)",
        "base_name": "국립공주대",
        "campus": "예산",
        "normalized_name": "국립공주대(예산)",
        "region": "충남",
        "website": "https://www.kongju.ac.kr",
        "phone": "041-850-0111",
        "address": "충남 예산군 예산읍 대학로 54",
        "directory_page": 643,
    },
    "국립공주대(천안)": {
        "id": "국립공주대-천안",
        "name": "국립공주대(천안)",
        "base_name": "국립공주대",
        "campus": "천안",
        "normalized_name": "국립공주대(천안)",
        "region": "충남",
        "website": "https://www.kongju.ac.kr",
        "phone": "041-850-0111",
        "address": "충남 천안시 서북구 천안대로 1223-24",
        "directory_page": 643,
    },
    "국립강릉원주대(강릉)": {
        "id": "국립강릉원주대-강릉",
        "name": "국립강릉원주대(강릉)",
        "base_name": "국립강릉원주대",
        "campus": "강릉",
        "normalized_name": "국립강릉원주대(강릉)",
        "region": "강원",
        "website": "https://www.gwnu.ac.kr",
        "phone": "033-640-2739, 2741",
        "address": "강원도 강릉시 죽헌길 7",
        "directory_page": 642,
    },
    "한서대(서산)": {
        "id": "한서대-서산",
        "name": "한서대(서산)",
        "base_name": "한서대",
        "campus": "서산",
        "normalized_name": "한서대(서산)",
        "region": "충남",
        "website": "https://www.hanseo.ac.kr",
        "phone": "041-660-1020",
        "address": "충남 서산시 해미면 한서1로 46",
        "directory_page": 646,
    },
    "호서대(아산)": {
        "id": "호서대-아산",
        "name": "호서대(아산)",
        "base_name": "호서대",
        "campus": "아산",
        "normalized_name": "호서대(아산)",
        "region": "충남",
        "website": "https://www.hoseo.ac.kr",
        "phone": "041-540-5114",
        "address": "충남 아산시 배방읍 호서로 79번길 20",
        "directory_page": 646,
    },
    "중원대(괴산)": {
        "id": "중원대-괴산",
        "name": "중원대(괴산)",
        "base_name": "중원대",
        "campus": "괴산",
        "normalized_name": "중원대(괴산)",
        "region": "충북",
        "website": "https://www.jwu.ac.kr",
        "phone": "043-830-8082~5",
        "address": "충북 괴산군 괴산읍 문무로 85",
        "directory_page": 646,
    },
}

CURATED_ADMISSIONS = {
    "경희대": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "297",
            "method": "교과56+출결7+봉사7+서류30",
            "csat_minimum": "인문·자연: 국,수,영,탐 중 2개 합 5, 한 5 / 의·치·한·약: 국,수,영,탐 중 3개 합 4, 한 5",
            "notes": "서울 본교 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 96},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "네오르네상스",
            "capacity": "584",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "의·치·한·약: 국,수,영,탐 중 3개 합 4, 한 5",
            "notes": "의예·한의예·치의예·약학은 4배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 155},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기회균형I",
            "capacity": "80",
            "method": "서류70+학생부30",
            "csat_minimum": "없음",
            "notes": "서울 본교 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기회균형II",
            "capacity": "54",
            "method": "서류70+학생부30",
            "csat_minimum": "없음",
            "notes": "서울 본교 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술우수자",
            "capacity": "262",
            "method": "논술100",
            "csat_minimum": "인문·자연: 국,수,영,탐 중 2개 합 5, 한 5 / 의예·치의예·한의예(자연)·약학: 국,수,영,탐 중 3개 합 4, 한 5 / 체육: 국,수,영,탐 중 1개 3 이내",
            "notes": "인문 133명, 자연 129명 기준",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 195},
                {"section_id": "essay", "section_title": "논술전형", "page": 201},
                {"section_id": "essay", "section_title": "논술전형", "page": 211},
            ],
        },
    ],
    "고려대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교추천",
            "capacity": "648",
            "method": "교과90+서류10",
            "csat_minimum": "인문·자연: 국,수,영,탐(1) 중 3개 합 7, 한 4 / 의대: 국,수,영,탐(1) 4개 합 5, 한 4",
            "notes": "서울 본교 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학업우수형",
            "capacity": "867",
            "method": "서류100",
            "csat_minimum": "전 모집단위: 국,수,영,탐(1) 중 4개 합 8, 한4 / 의과: 국,수,영,탐(1) 중 4개 합 5, 한4",
            "notes": "수능최저 적용",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 155},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "계열적합형",
            "capacity": "477",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "",
            "notes": "제시문 기반 면접 대표 전형",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 154},
            ],
        },
    ],
    "서울대": [
        {
            "admission_type": "학생부종합",
            "track_name": "지역균형",
            "capacity": "511",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "인문사회·자연과학·공학·간호·자유전공 등: 국,수,영,탐/과/직 중 3개 합 7",
            "notes": "모집단위별 반영 탐구/직탐 가능 여부가 다름",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 155},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반전형",
            "capacity": "1,424",
            "method": "1단계(2배수): 서류100 / 2단계: 1단계50+면접50",
            "csat_minimum": "없음",
            "notes": "대부분 모집단위 기준, 디자인·국악 등 일부 모집단위는 별도 방식 적용",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 154},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반전형(디자인)",
            "capacity": "7",
            "method": "1단계(2배수): 서류100 / 2단계: 면접100",
            "csat_minimum": "국,수,영,탐(2) 중 3개 합 7",
            "notes": "디자인과 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 174},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "사회통합",
            "capacity": "177",
            "method": "1단계(2배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "동양화·서양화·조소·공예, 성악·작곡·피아노·관현악, 디자인은 별도 실기/면접 방식 적용",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
    ],
    "연세대": [
        {
            "admission_type": "학생부교과",
            "track_name": "추천형",
            "capacity": "475+ (계약학과 25 별도 표기)",
            "method": "교과100",
            "csat_minimum": "인문: 국,수,탐(1) 중 2개 합 4, 영3, 한4 / 자연: 국,수(미/기),과(1) 중 2개 합 5, 영3, 한4 / 의·치·약: 국·수 포함 2개 각 1, 영3, 한4",
            "notes": "응용통계학과·생활과학대·간호대는 인문 또는 자연 기준 중 하나 충족",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "활동우수형",
            "capacity": "697",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "인문·광역: 국,수,탐(1) 중 2개 합 4, 한4, 영3, 국/수 포함 / 자연·공학: 국,수(미/기),과(1) 중 2개 합 5, 한4, 영3, 국/수 포함",
            "notes": "의·치·약은 더 높은 기준 적용",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 155},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "국제형-국내고",
            "capacity": "175",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "전 모집단위: 국,수,탐(1) 중 2개 합 5, 한4, 영3, 국/수 포함",
            "notes": "수능최저 적용",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 155},
            ],
        },
    ],
    "한양대": [
        {
            "admission_type": "학생부교과",
            "track_name": "추천형",
            "capacity": "330+ (계약학과 6 별도 표기)",
            "method": "교과90+서류10",
            "csat_minimum": "전 모집단위: 국,수,영,탐(1) 중 3개 합 7 / 의예과: 국,수,영,탐 중 3개 합 4",
            "notes": "서울 본교 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 149},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "추천형",
            "capacity": "291",
            "method": "서류100",
            "csat_minimum": "전 모집단위: 국,수,영,탐(1) 중 3개 합 7 / 의예과: 국,수,영,탐 중 3개 합 4",
            "notes": "수능최저 적용",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 149},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "면접형",
            "capacity": "136",
            "method": "1단계(7배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "수능최저 미적용",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
            ],
        },
    ],
    "성균관대": [
        {
            "admission_type": "학생부교과",
            "track_name": "추천인재",
            "capacity": "246",
            "method": "교과80+서류20",
            "csat_minimum": "인문·자연: 국,수,영,탐 중 3개 합 7 / 자유·글로벌(리더·경제·경영): 국,수,영,탐 중 3개 합 6",
            "notes": "제2외/한문 탐 1과목 대체 가능, 과 1과목 응시는 탐 2과목 평균 또는 과 상위 1과목 반영",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "서류형(융합인재)",
            "capacity": "160",
            "method": "서류100",
            "csat_minimum": "전 모집단위 국,수,영,탐 중 3개 합 6",
            "notes": "과(1)/탐(2) 평균 중 우수등급 반영, 제2외 탐(1) 대체 가능",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 156},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "면접형(성균인재)",
            "capacity": "164",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "글로벌융합학부·자유전공 7배수, 연출 5배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
    ],
    "중앙대": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "404",
            "method": "교과90+출결10",
            "csat_minimum": "전 모집단위 국,수,영,탐(1) 중 3개 합 7, 한 4 / 약학: 국,수,영,탐(1) 4개 합 5, 한 4",
            "notes": "영어 2등급은 1등급으로 인정",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "성장형인재",
            "capacity": "108",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "전 모집단위 국,수,영,탐(1) 중 3개 합 6, 한4 / 약학부·의학부 별도 강화 기준",
            "notes": "영어 2등급은 1등급으로 인정",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 156},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "융합형인재",
            "capacity": "260",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "의예는 1단계 3.5배수 후 2단계 1단계70+면접30",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "탐구형인재",
            "capacity": "427",
            "method": "1단계(3.5~5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
    ],
    "이화여대": [
        {
            "admission_type": "학생부교과",
            "track_name": "고교추천",
            "capacity": "368",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 5",
            "notes": "인문은 국, 자연은 수 응시 필수",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "미래인재-서류형",
            "capacity": "909",
            "method": "서류100",
            "csat_minimum": "전 모집단위 국,수,영,탐(1) 중 2개 합 5",
            "notes": "인문·예체능 국 포함, 자연·공학 수 포함, 국제학부는 영2 및 국 포함, 스크랜튼은 국수영탐(1) 중 3개 합 5",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 155},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "미래인재-면접형",
            "capacity": "209",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
    ],
    "서강대": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "175+ (계약학과 3 별도 표기)",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 3개 각 3, 한 4",
            "notes": "재학생 추천 전형으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반Ⅰ",
            "capacity": "473",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반Ⅱ",
            "capacity": "74",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
            ],
        },
    ],
    "서울시립대": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형선발",
            "capacity": "241",
            "method": "교과80+서류20",
            "csat_minimum": "국,수,영,탐(1) 중 3개 합 8, 한 4",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합Ⅰ",
            "capacity": "391",
            "method": "1단계(3배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합Ⅱ",
            "capacity": "99",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
    ],
    "한국외국어대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "200",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 4",
            "notes": "서울 본교 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합(면접형)",
            "capacity": "278",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계50+면접50",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합(서류형)",
            "capacity": "301",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
    ],
    "홍익대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천자",
            "capacity": "303",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 5, 한 4",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교생활우수자",
            "capacity": "467",
            "method": "서류100",
            "csat_minimum": "전 모집단위: 국,수,영,탐(1) 중 2개 합 5, 한 4",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 156},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "고른기회I",
            "capacity": "15",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "고른기회II",
            "capacity": "10",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "384",
            "method": "논술90+교과10",
            "csat_minimum": "인문·자연: 국,수,영,탐(1) 중 2개 합 5, 한 4",
            "notes": "인문 121명, 자연 263명 기준",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 197},
                {"section_id": "essay", "section_title": "논술전형", "page": 202},
                {"section_id": "essay", "section_title": "논술전형", "page": 213},
            ],
        },
    ],
    "숙명여대": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형선발",
            "capacity": "287",
            "method": "교과70+서류30",
            "csat_minimum": "약학: 국,수,영,탐(1) 중 3개 합 5 (수 포함)",
            "notes": "일반 모집단위 수능최저 미적용, 약학부만 적용으로 읽히는 구간",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "숙명인재(면접형)",
            "capacity": "361",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "소프트웨어인재",
            "capacity": "35",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기회균형",
            "capacity": "71",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "214",
            "method": "논술90+교과10",
            "csat_minimum": "인문·자연: 국,수,영,탐(1) 중 2개 합 5 / 약학: 국,수,영,탐(1) 중 3개 합 4(수 포함)",
            "notes": "인문 142명, 자연 72명 기준",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 197},
                {"section_id": "essay", "section_title": "논술전형", "page": 202},
                {"section_id": "essay", "section_title": "논술전형", "page": 212},
            ],
        },
    ],
    "숭실대": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "450",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 6",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "SSU미래인재(면접형)",
            "capacity": "492",
            "method": "1단계(3~3.5배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "",
            "notes": "기독교교육, 국어국문, 영어영문, 독어독문, 불어불문, 중어중문, 일어일문, 철학, 사학, 국제법무학은 3.5배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "SSU미래인재(서류형)",
            "capacity": "154",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
    ],
    "세종대": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "398",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 6 / 자유전공: 국,수,영,탐(1) 중 2개 합 5",
            "notes": "항공시스템공학은 별도 공군전형 단계 있음",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "세종인재(면접형)",
            "capacity": "360",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "세종인재(서류형)",
            "capacity": "228",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
    ],
    "건국대": [
        {
            "admission_type": "학생부교과",
            "track_name": "KU지역균형",
            "capacity": "346",
            "method": "교과70+서류30",
            "csat_minimum": "",
            "notes": "수능최저 미적용으로 읽히는 구간",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "KU자기추천",
            "capacity": "893",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기회균형",
            "capacity": "80",
            "method": "서류70+학생부30",
            "csat_minimum": "없음",
            "notes": "서울 본교 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "260",
            "method": "논술100",
            "csat_minimum": "인문·자연: 국,수,영,탐(1) 중 2개 합 5, 한 5 / 수의예: 국,수,영,탐(1) 중 3개 합 4, 한 5",
            "notes": "인문 101명, 자연 159명 기준. 정원외 65명 별도 표기",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 195},
                {"section_id": "essay", "section_title": "논술전형", "page": 201},
                {"section_id": "essay", "section_title": "논술전형", "page": 210},
            ],
        },
    ],
    "동국대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천인재",
            "capacity": "366",
            "method": "교과70+서류30",
            "csat_minimum": "없음",
            "notes": "서울 본교 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "Do Dream",
            "capacity": "590",
            "method": "1단계(3.5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "경영대학·컴퓨터AI학부 2.5배수, 일부 모집단위 3배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "불교추천인재",
            "capacity": "104",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "불교학부 2배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
    ],
    "국민대": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자(학교장추천)",
            "capacity": "591",
            "method": "교과100",
            "csat_minimum": "인문: 국,수,영,탐(1) 중 2개 합 6 / 자연: 국,수,영,과(1) 중 2개 합 6",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "국민프런티어",
            "capacity": "724",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "국제인재",
            "capacity": "15",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
            ],
        },
    ],
    "광운대": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "198",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "광운참빛인재전형Ⅰ-면접형",
            "capacity": "250",
            "method": "1단계(3.5배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "광운참빛인재전형Ⅱ-서류형",
            "capacity": "221",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 163},
            ],
        },
    ],
    "아주대": [
        {
            "admission_type": "학생부교과",
            "track_name": "고교추천",
            "capacity": "365",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 5",
            "notes": "의학: 국,수,영,탐 4개 합 6",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "ACE",
            "capacity": "560",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "의·약 계열 일부 적용",
            "notes": "수능최저 표기 △(의,약)",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "첨단융합인재",
            "capacity": "184",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
    ],
    "인하대(인천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "447",
            "method": "교과100",
            "csat_minimum": "적용",
            "notes": "2025년 졸업까지 지원 가능으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "인하미래인재(면접)",
            "capacity": "935",
            "method": "1단계(3.5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "의예과는 3배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "인하미래인재(서류)",
            "capacity": "252",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
            ],
        },
    ],
    "단국대(죽전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형선발",
            "capacity": "251",
            "method": "교과95+출결5",
            "csat_minimum": "적용",
            "notes": "학교장 추천 제한 없음으로 읽히는 구간",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "DKU인재-서류형",
            "capacity": "260",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "죽전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "DKU인재-면접형",
            "capacity": "162",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "죽전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
    ],
    "가톨릭대(성심)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "261",
            "method": "교과100",
            "csat_minimum": "적용",
            "notes": "의예과는 인적성면접을 P/F 자료로만 활용",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 144},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "잠재능력우수자(서류)",
            "capacity": "237",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "잠재능력우수자(면접)",
            "capacity": "232",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
    ],
    "명지대(용인)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "291",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "추천 인원은 모집요강 확인으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "명지인재면접",
            "capacity": "171",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "용인 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "명지인재서류",
            "capacity": "162",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "용인 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
    ],
    "상명대": [
        {
            "admission_type": "학생부교과",
            "track_name": "고교추천",
            "capacity": "319",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "국가안보",
            "capacity": "24",
            "method": "교과80+체력20+신체검사(합불)",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "상명인재",
            "capacity": "155",
            "method": "서류100 / 일부 모집단위 1단계(5배수): 서류100 / 2단계: 서류60+면접40",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준, 스포츠건강관리·조형예술은 1단계(5배수): 서류100 / 2단계: 서류60+면접40",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기회균형",
            "capacity": "70",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "98",
            "method": "논술90+교과10",
            "csat_minimum": "없음",
            "notes": "인문 44명, 자연 35명, 통합 19명 기준",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 196},
                {"section_id": "essay", "section_title": "논술전형", "page": 198},
                {"section_id": "essay", "section_title": "논술전형", "page": 201},
            ],
        },
    ],
    "상명대(천안)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과",
            "capacity": "394",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 10 / 간호: 수,영,탐(1) 중 2개 합 8",
            "notes": "천안 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 121},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "상명인재",
            "capacity": "156",
            "method": "서류100 / 일부 모집단위 1단계(5배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 기준, AR·VR미디어·문화예술경영 제외 예체능계는 1단계(5배수): 서류100 / 2단계: 1단계60+면접40",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 176},
            ],
        },
    ],
    "인천대(인천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "293",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "2022년 졸업자까지 지원 가능으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "자기추천",
            "capacity": "694",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "운동건강학부, 사범계열은 4배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
            ],
        },
    ],
    "서울여대": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "181",
            "method": "교과100",
            "csat_minimum": "적용",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "바롬인재서류",
            "capacity": "179",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "바롬인재면접",
            "capacity": "202",
            "method": "1단계(5배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
            ],
        },
    ],
    "덕성여대": [
        {
            "admission_type": "학생부교과",
            "track_name": "고교추천",
            "capacity": "145",
            "method": "교과100",
            "csat_minimum": "적용",
            "notes": "2019년 졸업자까지 지원 가능으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "덕성인재Ⅰ",
            "capacity": "115",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "덕성인재Ⅱ",
            "capacity": "240",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "글로벌융합, 과학기술, 자유전공은 4배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 151},
            ],
        },
    ],
    "성신여대": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "380",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 7",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "자기주도인재",
            "capacity": "525",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기회균형I",
            "capacity": "109",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "159",
            "method": "논술100",
            "csat_minimum": "인문: 국,수,영,탐(1) 중 2개 합 7 / 자연: 국,수,영,탐/직(1) 중 2개 합 7",
            "notes": "인문 74명, 자연 85명 기준",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 196},
                {"section_id": "essay", "section_title": "논술전형", "page": 201},
                {"section_id": "essay", "section_title": "논술전형", "page": 212},
            ],
        },
    ],
    "한성대": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "188",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수",
            "capacity": "222",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 7(야간 8)",
            "notes": "제2외/한문으로 탐구 1과목 대체 가능",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "한성인재",
            "capacity": "310",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "고른기회",
            "capacity": "45",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
            ],
        },
    ],
    "동덕여대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과우수자",
            "capacity": "196",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 6 / 약학: 국,수(미/기),과(1) 3개 합 6",
            "notes": "2025년 졸업자까지 지원 가능으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "동덕창의리더",
            "capacity": "255",
            "method": "1단계(3배수): 서류100 / 2단계: 면접60+1단계40",
            "csat_minimum": "약학: 국,수(미/기),과(1) 중 3개 합 6",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기회균형",
            "capacity": "12",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "264",
            "method": "논술100",
            "csat_minimum": "인문·자연: 국,수,영,탐(1) 중 2개 합 6",
            "notes": "인문 180명, 자연 84명 기준",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 196},
                {"section_id": "essay", "section_title": "논술전형", "page": 201},
                {"section_id": "essay", "section_title": "논술전형", "page": 211},
            ],
        },
    ],
    "삼육대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "100",
            "method": "교과100",
            "csat_minimum": "적용",
            "notes": "2005년 졸업자까지 지원 가능으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "세움인재",
            "capacity": "228",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "약학과 일부 적용",
            "notes": "수능최저 표기 △(약학)",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "S/W인재",
            "capacity": "30",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
    ],
    "서울과학기술대": [
        {
            "admission_type": "학생부교과",
            "track_name": "고교추천",
            "capacity": "509",
            "method": "교과100",
            "csat_minimum": "적용",
            "notes": "추천 인원은 모집요강 확인으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교생활우수자",
            "capacity": "486",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "창의융합인재",
            "capacity": "71",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
            ],
        },
    ],
    "한국항공대(고양)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "111",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "미래인재",
            "capacity": "146",
            "method": "1단계(3배수): 서류100 / 2단계: 서류70+면접30",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 172},
            ],
        },
    ],
    "한국공학대(시흥)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "196",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "2023년 졸업자까지 지원 가능으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "창의인재",
            "capacity": "256",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "융합인재",
            "capacity": "47",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
    ],
    "가천대(성남)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "358",
            "method": "1단계(7배수): 교과100 / 2단계: 1단계50+면접50",
            "csat_minimum": "없음",
            "notes": "추천 제한 없음으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 144},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "가천바람개비",
            "capacity": "365",
            "method": "1단계(4배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "없음",
            "notes": "성남 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기회균형",
            "capacity": "79",
            "method": "1단계(4배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "없음",
            "notes": "성남 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "883",
            "method": "논술100",
            "csat_minimum": "인문: 국,수,영,탐(1) 중 1개 3 / 자연: 국,수,영,탐(1) 중 1개 3 / 클라우드공학: 국,수(미/기),영,과(절사) 중 2개 합 4 / 한의예: 국,수(미/기),영,과 중 2개 각 1(과탐 모두 1)",
            "notes": "인문 291명, 자연 585명, 통합 7명 기준",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 195},
                {"section_id": "essay", "section_title": "논술전형", "page": 201},
                {"section_id": "essay", "section_title": "논술전형", "page": 210},
            ],
        },
    ],
    "가천대(메디컬)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부우수자",
            "capacity": "76",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 6",
            "notes": "바이오로직스 2개 합 5, 의예 3개 각 1, 약학 3개 합 5",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 96},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "31",
            "method": "1단계(7배수): 교과100 / 2단계: 1단계50+면접50",
            "csat_minimum": "없음",
            "notes": "메디컬 캠퍼스 자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 96},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "가천의약학",
            "capacity": "45",
            "method": "1단계(4배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 각 1 / 약학: 국,수(미/기),영,과 중 3개 합 5",
            "notes": "메디컬 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 156},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "가천바람개비",
            "capacity": "69",
            "method": "1단계(4배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "없음",
            "notes": "메디컬 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
            ],
        },
    ],
    "경기대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "317",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "추천 인원 20명",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 144},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "KGU학생부종합",
            "capacity": "622",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "수원 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "SW우수자",
            "capacity": "15",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "수원 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 169},
            ],
        },
    ],
    "을지대(성남)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "151",
            "method": "교과100",
            "csat_minimum": "적용",
            "notes": "안경광학, 의료경영은 수능최저 미적용으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "EU면접",
            "capacity": "112",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "성남 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "EU서류",
            "capacity": "93",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "성남 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
    ],
    "차 의과학대(포천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형선발",
            "capacity": "92",
            "method": "교과100",
            "csat_minimum": "약학부 일부 적용",
            "notes": "표기상 약학부만 수능최저 적용",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "CHA학생부종합",
            "capacity": "162",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "약학: 국,수,영,탐 중 3개 합 6, 수 포함",
            "notes": "수능최저 표기 △(약학)",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 156},
            ],
        },
    ],
    "한경국립대(안성)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형선발",
            "capacity": "82",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "2020년 졸업자까지 지원 가능으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "잠재력우수자",
            "capacity": "275",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "안성 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
    ],
    "안양대(안양)": [
        {
            "admission_type": "학생부교과",
            "track_name": "아리학생부교과",
            "capacity": "415",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "안양 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "아리학생부면접",
            "capacity": "173",
            "method": "1단계(6배수): 교과100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "안양 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "아리학생부종합",
            "capacity": "167",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "안양 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
    ],
    "평택대(평택)": [
        {
            "admission_type": "학생부교과",
            "track_name": "PTU추천",
            "capacity": "122",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "추천 인원은 모집요강 확인으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "PTU종합",
            "capacity": "73",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
    ],
    "신한대(의정부)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "293",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "의정부 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부우수자",
            "capacity": "158",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "의정부 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "신한국인",
            "capacity": "96",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "의정부 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
            ],
        },
    ],
    "신한대(동두천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "18",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "동두천 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부우수자",
            "capacity": "10",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "동두천 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "신한국인",
            "capacity": "12",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "동두천 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
            ],
        },
    ],
    "강남대(용인)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "185",
            "method": "교과100",
            "csat_minimum": "적용",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 144},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교생활우수자1",
            "capacity": "239",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교생활우수자2",
            "capacity": "55",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
    ],
    "대진대(포천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "213",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "윈윈대진",
            "capacity": "310",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
            ],
        },
    ],
    "수원대(화성)": [
        {
            "admission_type": "학생부교과",
            "track_name": "고교추천",
            "capacity": "112",
            "method": "교과60+면접40",
            "csat_minimum": "적용",
            "notes": "추천 제한 없음으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수",
            "capacity": "207",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 7 / 간호: 국,수,영,탐/직(1) 중 2개 합 6",
            "notes": "화성 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접위주교과",
            "capacity": "195",
            "method": "1단계(5배수): 교과80+출결10+봉사10 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "화성 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
    ],
    "성결대(안양)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수자",
            "capacity": "475",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "안양 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 98},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "SKU창의적인재",
            "capacity": "227",
            "method": "1단계(6배수): 교과100 / 2단계: 1단계40+면접60",
            "csat_minimum": "없음",
            "notes": "안양 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 98},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "미래인재",
            "capacity": "30",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "신학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 98},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "영암인재",
            "capacity": "119",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
            ],
        },
    ],
    "한세대(군포)": [
        {
            "admission_type": "학생부교과",
            "track_name": "면접우수자",
            "capacity": "53",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "군포 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "183",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "군포 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "한세인재",
            "capacity": "60",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 172},
            ],
        },
    ],
    "서울신학대(부천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "109",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "부천 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 98},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적",
            "capacity": "94",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "부천 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 98},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "H+인재",
            "capacity": "94",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
            ],
        },
    ],
    "경인교대(인천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "110",
            "method": "교과70+면접30",
            "csat_minimum": "적용",
            "notes": "2021년 졸업자까지 지원 가능으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 144},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "교직적성",
            "capacity": "226",
            "method": "서류70+면접30",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
            ],
        },
    ],
    "한신대(오산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "55",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부우수자",
            "capacity": "324",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "오산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "참인재",
            "capacity": "315",
            "method": "교과54+출결6+면접40",
            "csat_minimum": "없음",
            "notes": "오산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
    ],
    "한국외국어대(글로벌)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "375",
            "method": "교과100",
            "csat_minimum": "적용",
            "notes": "캠퍼스별 추천 10명, 2026년 졸업자까지 지원 가능으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "면접형",
            "capacity": "209",
            "method": "1단계(3배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "없음",
            "notes": "글로벌 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "서류형",
            "capacity": "274",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "글로벌 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
            ],
        },
    ],
    "중앙대(다빈치)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "498",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "다빈치 캠퍼스는 수능최저 미적용으로 표기",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "융합형인재",
            "capacity": "90",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "다빈치 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "탐구형인재",
            "capacity": "58",
            "method": "1단계(3.5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "다빈치 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
    ],
    "서울교대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "40",
            "method": "1단계(2배수): 교과100 / 2단계: 교과80+면접20",
            "csat_minimum": "국,수,영,탐 중 2개 합 6, 한 4",
            "notes": "재학생 대상, 추천 비율 3%",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 145},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "교직인성우수자",
            "capacity": "150",
            "method": "1단계(2배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "초등교육: 국,수,영,탐 중 2개 합 6, 한 4",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "국가보훈대상자",
            "capacity": "5",
            "method": "1단계(2배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "초등교육: 국,수,영,탐 중 2개 합 8, 한 4",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 155},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "농어촌학생",
            "capacity": "10",
            "method": "1단계(2배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "초등교육: 국,수,영,탐 중 2개 합 8, 한 4",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 165},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 155},
            ],
        },
    ],
    "성공회대": [
        {
            "admission_type": "학생부종합",
            "track_name": "열린인재",
            "capacity": "196",
            "method": "서류60+면접40",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "농어촌학생",
            "capacity": "6",
            "method": "학생부100",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {"section_id": "rural", "section_title": "농어촌학생 특별전형", "page": 279},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "기회균형선발",
            "capacity": "15",
            "method": "학생부100",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {
                    "section_id": "low-income",
                    "section_title": "기초생활수급자·차상위계층·한부모가족지원대상자 특별전형",
                    "page": 296,
                },
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "대안학교출신자",
            "capacity": "15",
            "method": "서류60+면접40",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 166},
            ],
        },
    ],
    "장로회신학대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부우수자",
            "capacity": "28",
            "method": "교과75.96+면접24.04",
            "csat_minimum": "없음",
            "notes": "인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 96},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "드림(PUTS인재)",
            "capacity": "32",
            "method": "서류60.61+면접39.39",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "사회기여 및 배려자",
            "capacity": "22",
            "method": "서류60.61+면접39.39",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
    ],
    "추계예술대": [
        {
            "admission_type": "학생부교과",
            "track_name": "미래인재",
            "capacity": "10",
            "method": "1단계(3배수): 교과100 / 2단계: 교과40+면접60",
            "csat_minimum": "없음",
            "notes": "융합예술학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 315},
            ],
        },
        {
            "admission_type": "수능",
            "track_name": "일반",
            "capacity": "38",
            "method": "수능100",
            "csat_minimum": "없음",
            "notes": "융합예술학부 유형2 기준",
            "source_refs": [
                {"section_id": "major-free-choice", "section_title": "전공자율선택제", "page": 552},
                {"section_id": "suneung", "section_title": "수능전형(예체능 제외)", "page": 231},
            ],
        },
        {
            "admission_type": "수능",
            "track_name": "기회균형(농어촌학생)",
            "capacity": "3",
            "method": "수능100",
            "csat_minimum": "없음",
            "notes": "나군 기준",
            "source_refs": [
                {"section_id": "rural", "section_title": "농어촌학생 특별전형", "page": 288},
            ],
        },
        {
            "admission_type": "수능",
            "track_name": "기회균형(장애인 등 대상자)",
            "capacity": "5",
            "method": "수능100",
            "csat_minimum": "없음",
            "notes": "나군 기준",
            "source_refs": [
                {"section_id": "disability", "section_title": "장애인 등 대상자 특별전형", "page": 325},
            ],
        },
    ],
    "한국체육대": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수자",
            "capacity": "4",
            "method": "교과80+출결20",
            "csat_minimum": "국,수,영,탐(1)/직 중 2개 합 6",
            "notes": "사회체육학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 221},
            ],
        },
    ],
    "성균관대(수원)": [
        {
            "admission_type": "학생부교과",
            "track_name": "추천인재",
            "capacity": "178",
            "method": "교과80+서류20",
            "csat_minimum": "국,수,영,탐 중 3개 합 7",
            "notes": "글로벌(바이오)·SW·반도체·에너지·전자전기 3개 합 6, 의예 4개 합 5",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 98},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "서류형(융합인재)",
            "capacity": "162",
            "method": "서류100",
            "csat_minimum": "적용",
            "notes": "수원 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "서류형(탐구인재)",
            "capacity": "237",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "수원 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "면접형(과학인재)",
            "capacity": "105",
            "method": "1단계(7배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "수원 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 170},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 152},
            ],
        },
    ],
    "단국대(천안)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과우수자",
            "capacity": "503",
            "method": "교과95+출결5",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 8",
            "notes": "간호 2개 합 5, 공공정책학(야) 국·수·영 중 1개 4",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "DKU인재-서류형",
            "capacity": "420",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 175},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "DKU인재-면접형",
            "capacity": "65",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "의/치/약 일부 적용",
            "notes": "천안 캠퍼스 기준, 수능최저 표기 △(의/치/약)",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 175},
            ],
        },
    ],
    "고려대(세종)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "307",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 6",
            "notes": "세종 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 108},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "270",
            "method": "논술100",
            "csat_minimum": "인문·자연: 국,수,영,탐(1) 중 2개 합 6 / 약학: 국,수(미/기),영,과 중 3개 합 5",
            "notes": "인문 99명, 자연 171명 기준. 약학 16명(일반 10, 지역 6) 포함",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 195},
                {"section_id": "essay", "section_title": "논술전형", "page": 201},
                {"section_id": "essay", "section_title": "논술전형", "page": 223},
            ],
        },
    ],
    "경희대(국제)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형",
            "capacity": "281",
            "method": "교과56+출결7+봉사7+서류30",
            "csat_minimum": "국,수,영,탐 중 2개 합 5, 한 5",
            "notes": "국제 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 97},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "디지털콘텐츠학과",
            "capacity": "5",
            "method": "학생부종합",
            "csat_minimum": "없음",
            "notes": "예체능계열 종합전형 모집단위 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 230},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술우수자",
            "capacity": "209",
            "method": "논술100",
            "csat_minimum": "자연: 국,수,영,탐 중 2개 합 5, 한 5",
            "notes": "인문 33명, 자연 176명 기준. 국제 캠퍼스 논술 수능최저 상세표에는 자연 기준이 명시됨",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 195},
                {"section_id": "essay", "section_title": "논술전형", "page": 211},
            ],
        },
    ],
    "연세대(미래)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자(일반형)",
            "capacity": "192",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐1,탐2 중 2개 합 7 또는 국,수,탐1,탐2 중 1개 2",
            "notes": "간호는 2개 합 5 또는 국·수 중 1개 1",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자(추천형)",
            "capacity": "83",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "미래 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "디자인예술학부",
            "capacity": "25",
            "method": "학생부종합",
            "csat_minimum": "없음",
            "notes": "수시에서 학생부종합전형으로만 선발한다고 표기",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 184},
            ],
        },
    ],
    "충남대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "1,103",
            "method": "교과100",
            "csat_minimum": "인문·사범: 국,수,영,탐(1) 중 3개 합 12 / 자연: 국,수,영,과(1) 중 3개 합 12",
            "notes": "의예 3개 합 4, 약학 3개 합 5, 수의예 3개 합 6",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "국어교육·수학교육·기술교육·화공교육",
            "capacity": "",
            "method": "1단계(3배수): 교과100 / 2단계: 1단계80+면접",
            "csat_minimum": "기술교육·화공교육: 국,수,영,과(1) 중 3개 합 12 / 국어교육·수학교육: 3개 합 10",
            "notes": "수학교육은 수 포함",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "국가안보교과",
            "capacity": "5",
            "method": "1단계(5배수): 교과100 / 2단계: 교과71.4+면접14.3+체력14.3",
            "csat_minimum": "국,수,영,탐(1) 중 3개 합 12",
            "notes": "국토안보 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합Ⅰ(면접(200))",
            "capacity": "124",
            "method": "1단계(2배수): 서류100 / 2단계: 1단계66.7+면접33.3",
            "csat_minimum": "일부 모집단위 적용",
            "notes": "대전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 154},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 157},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합Ⅰ(면접(300))",
            "capacity": "305",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계66.7+면접33.3",
            "csat_minimum": "의예 등 일부 모집단위 적용",
            "notes": "대전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 154},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 157},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합Ⅰ(서류)",
            "capacity": "278",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 154},
            ],
        },
    ],
    "충북대(청주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과",
            "capacity": "772",
            "method": "교과100",
            "csat_minimum": "인문·자율: 국,수,영,탐/직(1) 중 2개 합 7~8 / 자연: 국,수,영,탐(1) 중 2개 합 7~8",
            "notes": "자연은 수 포함, 간호 2개 합 6, 약학·제약 3개 합 6, 수의과 3개 합 7, 의예 3개 합 4",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합Ⅰ",
            "capacity": "537",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "청주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 177},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합Ⅱ",
            "capacity": "391",
            "method": "서류100",
            "csat_minimum": "일부 모집단위 적용",
            "notes": "청주 캠퍼스 기준, 수능최저 적용 계열/학과 별도 표기",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 177},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 157},
            ],
        },
    ],
    "경북대(대구)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "959",
            "method": "교과80+서류20",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 5~6",
            "notes": "IT·공과·첨단기술융합·공학첨단대학은 수 필수, 치의예 3개 합 4, 수의예·약학 3개 합 5",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반학생",
            "capacity": "883",
            "method": "서류100",
            "csat_minimum": "일부 모집단위 적용",
            "notes": "생환/과기 미적용 표기",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 178},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 159},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "395",
            "method": "1단계(4~5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "의/치/약 일부 적용",
            "notes": "대구 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 178},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재 학교장추천",
            "capacity": "3",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "적용",
            "notes": "의예, 치의예 기준 표기",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 177},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 159},
            ],
        },
    ],
    "제주대(제주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "533",
            "method": "교과100",
            "csat_minimum": "인문: 국,수,영,탐/직(절사) 중 2개 합 9 / 자연: 2개 합 10",
            "notes": "사범대 3개 합 10, 간호 3개 합 11, 초등교육 3개 합 8, 수의예·약학 3개 합 7, 의예 3개 합 6",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 117},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반학생",
            "capacity": "235",
            "method": "서류100 / 일부 모집단위 1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "사범, 초등교육, 수의, 간호, 약학은 단계별",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 205},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "47",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "제주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 205},
                {"section_id": "regional", "section_title": "지역인재전형", "page": 178},
            ],
        },
    ],
    "부산대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과",
            "capacity": "805",
            "method": "교과80+서류20",
            "csat_minimum": "인문: 국,수,영,탐(1) 중 2개 합 5, 한 4 / 경영: 3개 합 7, 한 4 / 자연: 2개 합 5, 한 4",
            "notes": "자연은 수 포함, 탐 2과목 응시 필수, 일부 과 1과목 응시 필수",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 115},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합",
            "capacity": "571",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "55",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "의/치/약/간 일부 적용",
            "notes": "약학은 1단계 4배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "약학",
            "capacity": "12",
            "method": "논술",
            "csat_minimum": "적용",
            "notes": "일반 6, 지역인재 6으로 표기",
            "source_refs": [
                {"section_id": "medical-overview", "section_title": "의약학계열 개요", "page": 130},
            ],
        },
    ],
    "우송대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과중심",
            "capacity": "783",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과면접",
            "capacity": "456",
            "method": "교과72+출결8+면접20",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "자기추천",
            "capacity": "98",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "종합서류형",
            "capacity": "182",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 154},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "종합면접형",
            "capacity": "132",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 154},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재Ⅱ",
            "capacity": "2",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 3445},
            ],
        },
    ],
    "한국기술교육대(천안)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "192",
            "method": "교과100",
            "csat_minimum": "인문: 국,수,영,탐(1) 중 2개 합 8 / 자연: 국,수,영,탐(1) 중 2개 합 8",
            "notes": "디자인공학은 필수영역 없음",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "창의인재(서류형)",
            "capacity": "124",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 176},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "창의인재(면접형)",
            "capacity": "110",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 176},
            ],
        },
    ],
    "한국교원대(청주)": [
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합우수자",
            "capacity": "318",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "적용",
            "notes": "초등/불어 미적용 표기",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 177},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "가군 모집",
            "capacity": "33",
            "method": "수능100",
            "csat_minimum": "",
            "notes": "교육 섹션 기준, 한국교원대(청주) 가군 33명 언급",
            "source_refs": [
                {"section_id": "education", "section_title": "교육계열", "page": 470},
            ],
        },
    ],
    "울산대(울산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반교과",
            "capacity": "685",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐(1) 중 1개 5",
            "notes": "아산아너스 2개 합 6, 미래엔지니어링 2개 합 10, 간호 2개 합 7(수 포함)",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "잠재역량",
            "capacity": "474",
            "method": "서류100 / 일부 모집단위 1단계(4배수): 서류100 / 2단계: 1단계50+면접50",
            "csat_minimum": "의예 일부 적용",
            "notes": "의예, 간호, 자율전공은 단계별",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재",
            "capacity": "17",
            "method": "서류100",
            "csat_minimum": "적용 가능",
            "notes": "의약학 지역인재 맥락의 전형",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 3447},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재 특별(기초생활수급자 등)",
            "capacity": "3",
            "method": "서류100",
            "csat_minimum": "적용 가능",
            "notes": "의약학 지역인재 맥락의 전형",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 3447},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "478",
            "method": "서류100 / 일부 모집단위 1단계(4배수): 서류100 / 2단계: 1단계50+면접50",
            "csat_minimum": "의예 일부 적용",
            "notes": "의예는 단계별",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
            ],
        },
    ],
    "원광대(익산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "1,212",
            "method": "교과90+출결10",
            "csat_minimum": "간호: 국,수,영,탐 중 3개 합 12",
            "notes": "익산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "군사학과",
            "capacity": "40",
            "method": "1단계(5배수): 교과90+출결10 / 2단계: 1단계25+면접50+체력25",
            "csat_minimum": "없음",
            "notes": "군사학과 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재종합(전북권)",
            "capacity": "42",
            "method": "서류100",
            "csat_minimum": "의예·치의예: 국,수,영,과(1) 중 3개 합 6 / 한의예: 국,수,영,과(1) 중 3개 합 6, 수 포함 / 약학: 국,수,영,과(1) 중 3개 합 7, 수 포함 / 간호: 국,수,영,탐(1) 중 3개 합 12",
            "notes": "전북권 기준, 한의예(인문)·한약학 모집 없음",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 3451},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 162},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재종합(호남권)",
            "capacity": "22",
            "method": "서류100",
            "csat_minimum": "의예·치의예: 국,수,영,과(1) 중 3개 합 6 / 한의예: 국,수,영,과(1) 중 3개 합 6, 수 포함 / 한의예(인문): 국,수,영,탐(1) 중 3개 합 6, 수 포함 / 한약학: 국,수,영,탐(1) 중 3개 합 9 / 간호: 국,수,영,탐(1) 중 3개 합 12",
            "notes": "호남권 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 3451},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 162},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재기회균형",
            "capacity": "3",
            "method": "서류100",
            "csat_minimum": "의예·치의예: 국,수,영,과(1) 중 3개 합 6 / 한의예: 국,수,영,과(1) 중 3개 합 6, 수 포함 / 한약학: 국,수,영,탐(1) 중 3개 합 9 / 간호: 국,수,영,탐(1) 중 3개 합 12",
            "notes": "지역인재 기회균형 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 3451},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 162},
            ],
        },
    ],
    "동아대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수자",
            "capacity": "1,006",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 1개 4",
            "notes": "석당인재·간호는 2개 합 7",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 115},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과진로우수자",
            "capacity": "234",
            "method": "교과80+서류20",
            "csat_minimum": "",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 115},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "잠재능력우수자",
            "capacity": "541",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "의예 일부 적용",
            "notes": "부산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 180},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교생활우수자",
            "capacity": "700",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 180},
            ],
        },
    ],
    "부산가톨릭대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수Ⅰ",
            "capacity": "204",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 115},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수Ⅱ",
            "capacity": "109",
            "method": "교과80+서류20",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 115},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "고교학생부",
            "capacity": "151",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 180},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "116",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 180},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "자기추천",
            "capacity": "73",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 180},
            ],
        },
    ],
    "남서울대(천안)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과+면접",
            "capacity": "370",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "989",
            "method": "교과90+봉사10",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재",
            "capacity": "23",
            "method": "교과90+봉사10",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 377},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합 서류형",
            "capacity": "91",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 175},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합 면접형",
            "capacity": "46",
            "method": "1단계(6배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 175},
            ],
        },
    ],
    "한남대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재교과우수자",
            "capacity": "16",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 379},
            ],
        },
    ],
    "한림대(춘천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "506",
            "method": "교과90+출결10",
            "csat_minimum": "간호: 국,수,영,탐 중 3개 합 10",
            "notes": "수(미/기) 반영 시 3개 합 12",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재",
            "capacity": "20",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "춘천 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 379},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교생활우수자",
            "capacity": "554",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "의학: 국,수(미/기),영,과 중 3개 합 4",
            "notes": "의학 모집단위 수능최저 적용",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 176},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 150},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "42",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "의학: 국,수(미/기),영,과 중 3개 합 5",
            "notes": "의학 5배수",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 176},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 150},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재_기초생활수급자 및 차상위계층",
            "capacity": "3",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "춘천 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 176},
            ],
        },
    ],
    "인제대(김해)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과",
            "capacity": "796",
            "method": "교과100",
            "csat_minimum": "간호: 국,수,영,탐(1) 중 2개 합 7 / 글로컬리더스: 국,수,영,과(1) 중 2개 합 7",
            "notes": "김해 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 117},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재Ⅰ",
            "capacity": "32",
            "method": "1단계(5배수): 교과100 / 2단계: 1단계67.5+면접32.5",
            "csat_minimum": "국,수(미/기),영,과(1) 각 2등급 이내",
            "notes": "의예 중심 지역인재 전형",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 359},
            ],
        },
    ],
    "국립목포대(목포)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과일반",
            "capacity": "700",
            "method": "교과90+출결10",
            "csat_minimum": "약학: 국,수(미/기),영,과(절사) 중 3개 합 7 / 간호: 국,수,영,탐/직(1) 중 1개 6",
            "notes": "약학은 수(미/기)와 과 필수 반영",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "종합일반",
            "capacity": "315",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "목포 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 248},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "38",
            "method": "1단계(6배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "약학 일부 적용",
            "notes": "목포 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 248},
                {"section_id": "regional", "section_title": "지역인재전형", "page": 379},
            ],
        },
    ],
    "국립순천대(순천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과일반",
            "capacity": "417",
            "method": "교과100",
            "csat_minimum": "간호: 국,수,영,탐(1) 중 2개 합 10 / 약학: 국,수(미/기),영,과(절사) 중 3개 합 7",
            "notes": "수학교육 수 4, 약학은 수(미/기), 과 필수 반영",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "종합면접",
            "capacity": "183",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "약학 일부 적용",
            "notes": "순천 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 248},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "종합서류",
            "capacity": "132",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "순천 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 248},
            ],
        },
    ],
    "전남대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "714",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 8",
            "notes": "공과·사범·자율은 2개 합 7, 경영·간호는 3개 합 9, 수의예·약학은 3개 합 6, 치의학은 3개 합 5",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 111},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "고교생활우수자Ⅰ",
            "capacity": "907",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "의학: 국,수(미/기),영,과 중 3개 합 5(수 포함) / 치의학: 국,수(미/기),영,과 중 3개 합 6(수 포함) / 약학·수의예: 국,수(미/기),영,과(1) 중 3개 합 7",
            "notes": "의학은 1단계 6배수. 의학·치의학·약학·수의예는 수(미/기), 과 응시 필수",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 248},
            ],
        },
    ],
    "전북대(전주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "1,348",
            "method": "교과100",
            "csat_minimum": "인문·생활과학: 국,수,영,탐(1) 중 2개 합 8 / 자연 일부: 2개 합 8",
            "notes": "융합자율전공1 2개 합 7, 간호·국어교육·영어교육 2개 합 6, 수학교육 2개 합 7",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "큰사람",
            "capacity": "487",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "의/약/치/간 일부 적용",
            "notes": "전주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 249},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재1",
            "capacity": "96",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "의/약/간 일부 적용",
            "notes": "전주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 249},
            ],
        },
    ],
    "전북대(특성화)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "52",
            "method": "교과100",
            "csat_minimum": "수의예: 국,수(미/기),영,과(1) 중 3개 합 7",
            "notes": "환경생명자원 2개 합 8, 융합자율전공2 2개 합 7",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "큰사람",
            "capacity": "15",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "수의예 일부 적용",
            "notes": "특성화 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 184},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재1",
            "capacity": "4",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "없음",
            "notes": "특성화 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 184},
            ],
        },
    ],
    "국립군산대(군산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "937",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "군산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 117},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반학생",
            "capacity": "351",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "군산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 183},
            ],
        },
    ],
    "전남대(여수)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "443",
            "method": "교과90+출결10",
            "csat_minimum": "수산생명의학: 국,수,영,탐/직(1) 중 2개 합 8",
            "notes": "여수 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 116},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "고교생활우수자Ⅱ",
            "capacity": "172",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "여수 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 183},
            ],
        },
    ],
    "우석대(완주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과면접",
            "capacity": "8",
            "method": "1단계: 교과100 / 2단계: 1단계70+면접30",
            "csat_minimum": "국,수,영,탐 중 3개 합 7 (수 포함)",
            "notes": "완주 캠퍼스 기준, 한의예 인문/자연 공통",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 417},
            ],
        },
    ],
    "경상국립대(진주)": [
        {
            "admission_type": "학생부종합",
            "track_name": "일반",
            "capacity": "685",
            "method": "서류100",
            "csat_minimum": "약학: 국,수(미/기),영,과 중 3개 합 6 / 수의예: 국,수,영,과 중 3개 합 7",
            "notes": "수의·사범·사회·심리·정치외교·미디어커뮤니케이션은 1단계(3배수): 서류100 / 2단계: 1단계80+면접20, 약학은 1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 161},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "331",
            "method": "서류100",
            "csat_minimum": "약학: 국,수(미/기),영,과 중 3개 합 6 / 수의예: 국,수,영,과 중 3개 합 7",
            "notes": "의약학계열 수능최저 상세표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 161},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "국가보훈대상자",
            "capacity": "3",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "사회통합",
            "capacity": "22",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기초생활수급자등",
            "capacity": "155",
            "method": "서류100",
            "csat_minimum": "약학: 국,수(미/기),영,과 중 3개 합 7 / 수의예: 국,수,영,과 중 3개 합 7",
            "notes": "의약학계열 수능최저 상세표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 161},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "평생학습자",
            "capacity": "5",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(수의예)",
            "capacity": "10",
            "method": "교과100",
            "csat_minimum": "국,수,영,과(절사) 중 3개 합 6",
            "notes": "진주 캠퍼스 기준, 수의예 계열",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 428},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반(치의예)",
            "capacity": "3",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "국,수(미/기),영,과(절사) 중 3개 합 6",
            "notes": "진주 캠퍼스 기준, 치의예 계열",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 400},
            ],
        },
    ],
    "경상국립대(칠암)": [
        {
            "admission_type": "학생부종합",
            "track_name": "일반",
            "capacity": "20",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 6",
            "notes": "의예는 1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 182},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 161},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "21",
            "method": "서류100",
            "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 6",
            "notes": "의예는 1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 182},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 161},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기초생활수급자등",
            "capacity": "10",
            "method": "서류100",
            "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 6",
            "notes": "의예는 1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 182},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 161},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "52",
            "method": "교과100",
            "csat_minimum": "간호: 국,수,영,탐(1) 중 2개 합 8 / 의예: 국,수(미/기),영,과(절사) 중 3개 합 4",
            "notes": "칠암 캠퍼스 간호·의예 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "13",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "칠암 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 379},
            ],
        },
    ],
    "국립부경대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "207",
            "method": "교과90+출결10",
            "csat_minimum": "인문: 국,수,영,탐(1) 중 2개 합 8 / 자연: 2개 합 9",
            "notes": "자연은 수 포함, 수(확) 선택 시 1등급 하향",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수인재",
            "capacity": "1,480",
            "method": "교과90+출결10",
            "csat_minimum": "",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "사회적배려대상자Ⅲ",
            "capacity": "1",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 기준, 특수전형",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 380},
            ],
        },
    ],
    "국립창원대(창원)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학업성적우수자",
            "capacity": "438",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 7~9",
            "notes": "독문·일문·행정(야) 등 일부 모집단위 수능최저 없음",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "11",
            "method": "서류100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 8",
            "notes": "창원 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 380},
            ],
        },
    ],
    "고신대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반고",
            "capacity": "217",
            "method": "교과100",
            "csat_minimum": "간호: 국,수,영,탐(1) 중 2개 합 7",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "의예",
            "capacity": "25",
            "method": "1단계(10배수): 교과100 / 2단계: 1단계90+면접10",
            "csat_minimum": "국,수,영,과(1) 중 3개 합 4",
            "notes": "수(확) 선택자는 3개 합 3, 수 포함",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "유아교육·기독교육",
            "capacity": "25",
            "method": "교과90+인적성10",
            "csat_minimum": "없음",
            "notes": "유아교육, 기독교육 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "신학",
            "capacity": "18",
            "method": "교과90+교리10",
            "csat_minimum": "없음",
            "notes": "신학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재기회균형",
            "capacity": "3",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 기준, 특수전형",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 379},
            ],
        },
    ],
    "동의대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반고교과",
            "capacity": "1,893",
            "method": "교과100",
            "csat_minimum": "경찰행정·물리치료·방사선·임상병리·치위생: 국,수,영,탐(1) 중 2개 합 8",
            "notes": "간호 2개 합 7, 한의예 3개 합 5",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 115},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재종합",
            "capacity": "15",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 380},
            ],
        },
    ],
    "국립강릉원주대(원주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "해람교과",
            "capacity": "208",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "원주 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "4",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "원주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 379},
            ],
        },
    ],
    "나사렛대(천안)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "641",
            "method": "교과100",
            "csat_minimum": "간호: 국,수,영,탐 중 2개 합 7",
            "notes": "천안 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재Ⅱ",
            "capacity": "16",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "천안 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 380},
            ],
        },
    ],
    "대구대(경산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "면접",
            "capacity": "109",
            "method": "1단계(10배수): 교과90+출결10 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "경산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 107},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "1,748",
            "method": "교과90+출결10",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 8",
            "notes": "경산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 107},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역기회균형",
            "capacity": "3",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "경산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 380},
            ],
        },
    ],
    "대구한의대(경산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "면접",
            "capacity": "29",
            "method": "교과75+면접25",
            "csat_minimum": "없음",
            "notes": "경산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 107},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "간호",
            "capacity": "14",
            "method": "1단계(10배수): 교과100 / 2단계: 1단계75+면접25",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 8",
            "notes": "간호 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 107},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "412",
            "method": "교과100",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 7",
            "notes": "한의예 인문 3개 합 4, 한의예 자연 3개 합 5",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 107},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "17",
            "method": "서류100",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 8",
            "notes": "경산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 380},
            ],
        },
    ],
    "국립공주대(공주)": [
        {
            "admission_type": "학생부종합",
            "track_name": "일반전형",
            "capacity": "551",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "공주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 177},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재",
            "capacity": "18",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 7",
            "notes": "공주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 377},
            ],
        },
    ],
    "국립공주대(예산)": [
        {
            "admission_type": "학생부종합",
            "track_name": "일반전형",
            "capacity": "102",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "예산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-comprehensive", "section_title": "학생부종합전형", "page": 177},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "134",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 11등급",
            "notes": "예산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-subject", "section_title": "학생부교과전형", "page": 108},
            ],
        },
    ],
    "국립공주대(천안)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "401",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 10등급",
            "notes": "천안 캠퍼스 기준",
            "source_refs": [
                {"section_id": "student-record-subject", "section_title": "학생부교과전형", "page": 109},
            ],
        },
    ],
    "국립강릉원주대(강릉)": [
        {
            "admission_type": "학생부교과",
            "track_name": "해람교과",
            "capacity": "474",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "강릉 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 94},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "해람인재",
            "capacity": "286",
            "method": "서류100 / 치의예: 1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "치의예: 국,수,영,과(1) 중 3개 합 6(수 포함)",
            "notes": "강릉 캠퍼스 기준, 치의예만 단계별 면접 운영",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 172},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 405},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "88",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "강릉 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 173},
                {"section_id": "regional", "section_title": "지역인재전형", "page": 336},
            ],
        },
    ],
    "가톨릭관동대(강릉)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "840",
            "method": "교과100",
            "csat_minimum": "의학: 국,수(미/기),영,과(절사) 중 3개 합 5 / 간호: 국,수,영,탐(절사) 중 2개 합 9",
            "notes": "강릉 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "5",
            "method": "서류100",
            "csat_minimum": "국,수,영,탐(절사) 중 2개 합 9",
            "notes": "강릉 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 379},
            ],
        },
    ],
    "순천향대(아산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "685",
            "method": "교과100",
            "csat_minimum": "국,수,영 중 1개 5",
            "notes": "의료과학대 1개 4, 간호 3개 합 10, 의예 4개 합 6",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "충청형지역인재",
            "capacity": "10",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "아산 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 380},
            ],
        },
    ],
    "중원대(괴산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반Ⅰ",
            "capacity": "335",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "괴산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반Ⅱ",
            "capacity": "90",
            "method": "교과80+면접20 / 간호: 교과60+면접40",
            "csat_minimum": "없음",
            "notes": "괴산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "실기/실적",
            "track_name": "실기중심",
            "capacity": "8",
            "method": "실기90+학생부10",
            "csat_minimum": "없음",
            "notes": "운동레저학부 유형2 기준",
            "source_refs": [
                {"section_id": "major-free-choice", "section_title": "전공자율선택제", "page": 512},
            ],
        },
    ],
    "청주교대(청주)": [
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "132",
            "method": "1단계(2배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "청주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 479},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "일반전형",
            "capacity": "68",
            "method": "수능100",
            "csat_minimum": "",
            "notes": "2027학년도부터 면접 폐지",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 483},
            ],
        },
    ],
    "공주교대(공주)": [
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재선발",
            "capacity": "123",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "공주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 479},
            ],
        },
    ],
    "광주교대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재",
            "capacity": "50",
            "method": "학생부교과80+서류20",
            "csat_minimum": "없음",
            "notes": "광주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 479},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "50",
            "method": "1단계(2.5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "광주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 479},
            ],
        },
    ],
    "대구교대(대구)": [
        {
            "admission_type": "학생부종합",
            "track_name": "경북지역인재",
            "capacity": "127",
            "method": "1단계(2배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "대구 캠퍼스 기준",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 479},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "대구지역인재",
            "capacity": "90",
            "method": "1단계(2배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "대구 캠퍼스 기준",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 479},
            ],
        },
    ],
    "진주교대(진주)": [
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "123",
            "method": "1단계(2.5배수): 서류100 / 2단계: 1단계63.6+면접36.4",
            "csat_minimum": "없음",
            "notes": "진주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 479},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "일반학생",
            "capacity": "102",
            "method": "수능100",
            "csat_minimum": "",
            "notes": "나군 기준",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 483},
            ],
        },
    ],
    "춘천교대(춘천)": [
        {
            "admission_type": "학생부종합",
            "track_name": "강원교육인재",
            "capacity": "60",
            "method": "서류100",
            "csat_minimum": "국,수,영,탐(1) 3개 합 10, 한 4",
            "notes": "춘천 캠퍼스 기준",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 479},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "일반학생",
            "capacity": "120",
            "method": "수능100",
            "csat_minimum": "수능 최저 3개 합 14",
            "notes": "한국사 등급별 가산점 부여",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 483},
            ],
        },
    ],
    "부산교대(부산)": [
        {
            "admission_type": "정시",
            "track_name": "일반전형",
            "capacity": "122",
            "method": "수능95.2+면접4.8",
            "csat_minimum": "",
            "notes": "표준점수 반영",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 483},
            ],
        },
    ],
    "강서대": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "66",
            "method": "교과80+면접20",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "106",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
    ],
    "서경대": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "102",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과균형",
            "capacity": "204",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 8",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "군사학과",
            "capacity": "40",
            "method": "교과70+면접20+체력10",
            "csat_minimum": "없음",
            "notes": "군사 모집단위 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "214",
            "method": "논술100",
            "csat_minimum": "없음",
            "notes": "약술형 논술, 인문·자연 통합 모집인원 기준",
            "source_refs": [
                {"section_id": "essay", "section_title": "논술전형", "page": 196},
                {"section_id": "essay", "section_title": "논술전형", "page": 201},
            ],
        },
        {
            "admission_type": "기회균형",
            "track_name": "기회균형1",
            "capacity": "22",
            "method": "학생부100",
            "csat_minimum": "",
            "notes": "국가보훈·기초생활수급자 계열 통합전형",
            "source_refs": [
                {"section_id": "opportunity", "section_title": "기회균형 선발 대상자(통합)전형", "page": 269},
            ],
        },
    ],
    "한국성서대": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "70",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수자",
            "capacity": "52",
            "method": "교과80+면접20",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "고른기회",
            "capacity": "4",
            "method": "학생부70+면접30",
            "csat_minimum": "없음",
            "notes": "농어촌, 기초생활수급자·차상위, 만학도 포함",
            "source_refs": [
                {"section_id": "opportunity-integrated", "section_title": "기회균형 선발 대상자(통합)전형", "page": 266},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "농어촌고교출신자",
            "capacity": "5",
            "method": "학생부70+면접30",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {"section_id": "rural", "section_title": "농어촌학생 특별전형", "page": 279},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "기초생활수급자 및 차상위",
            "capacity": "7",
            "method": "학생부70+면접30",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {
                    "section_id": "low-income",
                    "section_title": "기초생활수급자·차상위계층·한부모가족지원대상자 특별전형",
                    "page": 296,
                },
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "특수교육대상자",
            "capacity": "10",
            "method": "학생부70+면접30",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {"section_id": "disability", "section_title": "장애인 등 대상자 특별전형", "page": 319},
            ],
        },
    ],
    "건양대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반(교과)",
            "capacity": "536",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(최저)",
            "capacity": "23",
            "method": "교과100",
            "csat_minimum": "국,수,영,과(절사) 중 3개 합 4",
            "notes": "의예과 기준",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "2027학년도 의치약한수계열 특징", "page": 393},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합",
            "capacity": "174",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 176},
            ],
        },
    ],
    "상지대(원주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과일반",
            "capacity": "7",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(절사) 중 3개 합 4 (수(미/기) 반영 시 5등급)",
            "notes": "한의예 인문·자연 통합 기준",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "2027학년도 의치약한수계열 특징", "page": 423},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "종합일반",
            "capacity": "15",
            "method": "교과20+서류80",
            "csat_minimum": "국,수,영,탐(절사) 중 3개 합 4 (수(미/기) 반영 시 3개 합 5)",
            "notes": "한의예 인문·자연 통합 기준",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "2027학년도 의치약한수계열 특징", "page": 424},
            ],
        },
    ],
    "대전대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과중점",
            "capacity": "10",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐 중 3개 합 5, 한 5 (수 포함)",
            "notes": "한의예 인문·자연 통합 기준",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "2027학년도 의치약한수계열 특징", "page": 423},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "혜화인재",
            "capacity": "8",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계60+면접40",
            "csat_minimum": "국,수,영,탐(절사) 중 3개 합 6, 한 5 (수 포함)",
            "notes": "한의예 인문·자연 통합 기준",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "2027학년도 의치약한수계열 특징", "page": 424},
            ],
        },
    ],
    "영남대(경산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "1,414",
            "method": "교과90+출결5+서류평가5",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 8~9 / 의예: 국,수,영,과(1) 합 5 / 약학: 국,수,영,과(1) 중 3개 합 5",
            "notes": "자연은 수(미/기) 반영 시 1등급 상향. 의예·약학은 과 2과목 응시",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "창의인재",
            "capacity": "43",
            "method": "1단계(5배수): 교과90+출결5+서류5 / 2단계: 1단계70+면접30",
            "csat_minimum": "자유: 국,수,영,탐(1) 중 2개 합 8 / 의예: 국,수,영,과(1) 합 5",
            "notes": "의예는 7배수, 의예는 과 2과목 응시",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "군사학",
            "capacity": "30",
            "method": "1단계(5배수): 교과90+출결5+서류5 / 2단계: 1단계70+면접20+체력10",
            "csat_minimum": "국,수,영 중 1개 5",
            "notes": "군사학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(음악)",
            "capacity": "2",
            "method": "교과90+출결5+기타5",
            "csat_minimum": "없음",
            "notes": "음악학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 589},
            ],
        },
    ],
    "경성대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반계고교",
            "capacity": "811",
            "method": "교과100",
            "csat_minimum": "약학: 국,수(미/기),영,과(1) 중 3개 합 5 / 간호: 국,수,영,탐(1) 중 2개 합 8",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반계고교과(영상애니메이션·패션디자인)",
            "capacity": "28",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "영상애니메이션학부 10명, 패션디자인학과 18명",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 595},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재(영상애니메이션)",
            "capacity": "8",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "영상애니메이션학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 595},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반계고교과(뮤지컬·영화)",
            "capacity": "16",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "뮤지컬전공 5명, 영화전공 11명",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 598},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교생활우수자",
            "capacity": "30",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "영상애니메이션학부 10명, 패션디자인학과 15명, 스포츠건강학과 5명",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 604},
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 615},
            ],
        },
    ],
    "명지대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "171",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과면접",
            "capacity": "134",
            "method": "1단계(5배수): 교과100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "명지인재면접",
            "capacity": "198",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "명지인재서류",
            "capacity": "197",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "크리스찬리더",
            "capacity": "26",
            "method": "1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "사회적배려대상자",
            "capacity": "19",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "서울 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 164},
            ],
        },
    ],
    "경기대(수원)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "283",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "수원 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 97},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수자",
            "capacity": "255",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 7, 한 6",
            "notes": "수원 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 97},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "185",
            "method": "논술90+교과10",
            "csat_minimum": "없음",
            "notes": "인문 모집인원 기준",
            "source_refs": [
                {"section_id": "regular-03", "section_title": "논술전형", "page": 195},
                {"section_id": "regular-03", "section_title": "논술전형", "page": 198},
            ],
        },
    ],
    "동국대(WISE)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학업성적우수자",
            "capacity": "41",
            "method": "교과100",
            "csat_minimum": "국,수,과(1) 3개 합 5",
            "notes": "한의예 인문·자연 통합 기준",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "2027학년도 의치약한수계열 특징", "page": 423},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "참사람",
            "capacity": "8",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "국,수,영,과(1) 중 3개 합 5",
            "notes": "한의예 자연 기준",
            "source_refs": [
                {"section_id": "medical-features", "section_title": "2027학년도 의치약한수계열 특징", "page": 424},
            ],
        },
    ],
    "KAIST": [
        {
            "admission_type": "학생부종합",
            "track_name": "창의도전",
            "capacity": "200명 내외",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "면접 미실시",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 486},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 487},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반",
            "capacity": "350명 내외",
            "method": "서류40+면접60",
            "csat_minimum": "",
            "notes": "개인별 구술면접 실시",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 486},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 487},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "수능우수자",
            "capacity": "15명 내외",
            "method": "수능100",
            "csat_minimum": "수학: 미적분/기하, 과탐 2과목(서로 다른 분야)",
            "notes": "과탐Ⅱ 5% 가산",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 487},
            ],
        },
    ],
    "GIST": [
        {
            "admission_type": "학생부종합",
            "track_name": "일반",
            "capacity": "150명 내외",
            "method": "서류60+면접40",
            "csat_minimum": "",
            "notes": "5~6배수 내외 서류평가 후 면접",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 487},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 488},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교장추천",
            "capacity": "40명 내외",
            "method": "서류60+면접40",
            "csat_minimum": "",
            "notes": "고교별 2명 이내 추천",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 487},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 488},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "수능우수자",
            "capacity": "15명 내외",
            "method": "수능100",
            "csat_minimum": "수학: 미적분/기하, 과탐 2과목(서로 다른 분야)",
            "notes": "국20:수30:영20:과30, 과탐Ⅱ 10% 가산",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 488},
            ],
        },
    ],
    "DGIST": [
        {
            "admission_type": "학생부종합",
            "track_name": "일반",
            "capacity": "100명 내외",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "면접 미실시",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 488},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 489},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교장추천",
            "capacity": "65명 내외",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "면접 미실시, 고교별 2명 이내 추천",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 488},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 489},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "수능우수자",
            "capacity": "5명 내외",
            "method": "수능100",
            "csat_minimum": "수학: 미적분/기하",
            "notes": "과탐Ⅱ 5% 가산",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 488},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 489},
            ],
        },
    ],
    "UNIST": [
        {
            "admission_type": "학생부종합",
            "track_name": "일반",
            "capacity": "310명 내외",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "면접 미실시",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 489},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 490},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "65명 내외",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "울산 지역인재",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 489},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 490},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "탐구우수",
            "capacity": "50명 내외",
            "method": "서류50+면접50",
            "csat_minimum": "",
            "notes": "창의적 탐구능력 및 수학능력 평가",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 489},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 490},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "수능우수자",
            "capacity": "15명 내외",
            "method": "수능100",
            "csat_minimum": "수학: 미적분/기하, 과탐 2과목(서로 다른 분야)",
            "notes": "과탐Ⅱ 5% 가산",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 489},
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 490},
            ],
        },
    ],
    "건국대(글로컬)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수",
            "capacity": "404",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "글로컬 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "지역인재",
            "capacity": "27",
            "method": "수능100",
            "csat_minimum": "",
            "notes": "다군, 의약학 지역인재 정시 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재 특별전형", "page": 363},
            ],
        },
    ],
    "동신대(나주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반(인문·자연)",
            "capacity": "842",
            "method": "교과80+출결20",
            "csat_minimum": "간호: 국,수,영,탐(1) 중 2개 합 11 / 물리치료: 국,수,영,탐(1) 중 2개 합 13 / 한의예: 국,수,영,탐(1) 중 3개 합 5",
            "notes": "학생부교과전형 일반 인문·자연 기준",
            "source_refs": [
                {"section_id": "student-record-subject", "section_title": "학생부교과전형", "page": 119},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접",
            "capacity": "143",
            "method": "교과56+출결14+면접30",
            "csat_minimum": "없음",
            "notes": "학생부교과전형 면접 인문·자연 기준",
            "source_refs": [
                {"section_id": "student-record-subject", "section_title": "학생부교과전형", "page": 119},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역학생1",
            "capacity": "16",
            "method": "교과80+출결20",
            "csat_minimum": "한의예: 국,수,영,탐(1) 중 3개 합 5",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 341},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 423},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역학생2",
            "capacity": "94",
            "method": "교과80+출결20",
            "csat_minimum": "물리치료: 국,수,영,탐(1) 중 2개 합 13 / 한의예: 국,수,영,탐(1) 중 3개 합 5",
            "notes": "지역인재전형 표 기준. 한의예 세부 기준은 의약학계열 한의예 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 341},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 423},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역학생기회균형",
            "capacity": "2",
            "method": "교과80+출결20",
            "csat_minimum": "한의예: 국,수,영,탐(1) 중 3개 합 5",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 341},
                {"section_id": "medical-features", "section_title": "의약학계열 특징", "page": 423},
            ],
        },
        {
            "admission_type": "기회균형",
            "track_name": "기초생활수급자 및 차상위계층",
            "capacity": "63",
            "method": "학생부100",
            "csat_minimum": "",
            "notes": "기초생활수급자 및 차상위계층 특별전형 표 기준",
            "source_refs": [
                {"section_id": "low-income", "section_title": "기초생활수급자 및 차상위계층 특별전형", "page": 303},
            ],
        },
        {
            "admission_type": "농어촌",
            "track_name": "농어촌학생",
            "capacity": "2",
            "method": "학생부100",
            "csat_minimum": "한의예: 국,수,영,탐(1) 중 3개 합 6",
            "notes": "농어촌학생 특별전형 한의예 표 기준",
            "source_refs": [
                {"section_id": "rural", "section_title": "농어촌학생 특별전형", "page": 294},
            ],
        },
        {
            "admission_type": "특성화고",
            "track_name": "특성화고교졸업자",
            "capacity": "15",
            "method": "학생부100",
            "csat_minimum": "",
            "notes": "특성화고교졸업자 특별전형 표 기준",
            "source_refs": [
                {"section_id": "vocational", "section_title": "특성화고교졸업자 특별전형", "page": 317},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(뮤지컬·실용음악)",
            "capacity": "10",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "뮤지컬·실용음악학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 590},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접(생활체육)",
            "capacity": "10",
            "method": "교과56+출결14+면접30",
            "csat_minimum": "없음",
            "notes": "생활체육학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(생활체육)",
            "capacity": "20",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "생활체육학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
    ],
    "경일대(경산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "면접(인문·자연)",
            "capacity": "148",
            "method": "교과63+출결7+면접30",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 9",
            "notes": "경산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(인문·자연)",
            "capacity": "236",
            "method": "교과90+출결10",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 9",
            "notes": "경산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재교과",
            "capacity": "17",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 9",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 345},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접(디자인융합학부)",
            "capacity": "8",
            "method": "교과63+출결7+면접30",
            "csat_minimum": "없음",
            "notes": "디자인융합학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 594},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(디자인융합학부)",
            "capacity": "12",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "디자인융합학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 594},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접(스포츠복지학과)",
            "capacity": "12",
            "method": "교과63+출결7+면접30",
            "csat_minimum": "없음",
            "notes": "스포츠복지학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 600},
            ],
        },
    ],
    "한라대(원주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "성인학습자(문화예술)",
            "capacity": "15",
            "method": "교과58.95+출결6.55+면접34.5",
            "csat_minimum": "없음",
            "notes": "문화예술학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 592},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "성인학습자(골프산업)",
            "capacity": "20",
            "method": "교과59+출결6.5+면접34.5",
            "csat_minimum": "없음",
            "notes": "골프산업학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 598},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(면접중심)",
            "capacity": "14",
            "method": "교과59+출결6.5+면접34.5",
            "csat_minimum": "없음",
            "notes": "스포츠학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 598},
            ],
        },
    ],
    "용인대(용인)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(인문·자연)",
            "capacity": "195",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "용인 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수자",
            "capacity": "80",
            "method": "교과100",
            "csat_minimum": "국,수,영 중 2개 합 8 / 경찰행정: 국,수,영 3개 합 9",
            "notes": "용인 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "자율전공",
            "capacity": "155",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "용인 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(경호)",
            "capacity": "23",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "경호학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 598},
            ],
        },
    ],
    "KENTECH": [
        {
            "admission_type": "학생부종합",
            "track_name": "일반",
            "capacity": "90명",
            "method": "1단계50+2단계50",
            "csat_minimum": "",
            "notes": "1단계 서류평가 100%(5배수), 2단계 창의성 면접",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 490},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "고른기회",
            "capacity": "10명",
            "method": "1단계50+2단계50",
            "csat_minimum": "",
            "notes": "저소득 학생 3명, 농어촌 학생 7명",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 490},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "수능우수자",
            "capacity": "10명",
            "method": "수능100",
            "csat_minimum": "수학: 미적분/기하, 과탐 2과목",
            "notes": "영어 2등급, 한국사 4등급부터 감점",
            "source_refs": [
                {"section_id": "science-specialized", "section_title": "이공계 특성화 대학", "page": 490},
            ],
        },
    ],
    "경남대(창원)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "973",
            "method": "교과90+출결10",
            "csat_minimum": "간호: 국,수,영,탐(1) 중 2개 합 9 / 물리치료: 국,수,영,탐(1) 중 2개 합 10",
            "notes": "창원 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반면접(인문·자연)",
            "capacity": "78",
            "method": "1단계(4배수): 교과90+출결10 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "창원 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "군사학과",
            "capacity": "20",
            "method": "1단계(5배수): 교과90+출결10 / 2단계: 1단계70+면접20+체력10",
            "csat_minimum": "국,수,영 중 1개 5",
            "notes": "군사학과 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반면접(음악교육과)",
            "capacity": "22",
            "method": "1단계(4배수): 교과90+출결10 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "음악교육과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 590},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반면접(미술교육과)",
            "capacity": "15",
            "method": "1단계(4배수): 교과90+출결10 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "미술교육과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 596},
            ],
        },
    ],
    "광주대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(인문·자연)",
            "capacity": "789",
            "method": "교과90+출결10",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 11",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "나눔인재(인문·자연)",
            "capacity": "162",
            "method": "교과60+출결10+봉사30",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역학생",
            "capacity": "100",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 330},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(산업디자인)",
            "capacity": "15",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "산업디자인학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 596},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "나눔인재(문화산업대학 예체능)",
            "capacity": "51",
            "method": "교과60+출결10+봉사30",
            "csat_minimum": "없음",
            "notes": "문화산업대학(예체능) 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 609},
            ],
        },
    ],
    "동서대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반계교과",
            "capacity": "561",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부면접(인문·자연)",
            "capacity": "257",
            "method": "교과62.5+면접37.5",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "고교생활우수자(계열2)",
            "capacity": "33",
            "method": "교과88.9+출결11.1",
            "csat_minimum": "없음",
            "notes": "계열2_디자인/건축/게임/애니메이션/웹툰 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 609},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부면접(계열2)",
            "capacity": "54",
            "method": "교과62.5+면접37.5",
            "csat_minimum": "없음",
            "notes": "계열2_디자인/건축/게임/애니메이션/웹툰 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 609},
            ],
        },
    ],
    "신경주대(경주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반(인문·자연)",
            "capacity": "260",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "경주 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접",
            "capacity": "165",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "경주 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(악기제작)",
            "capacity": "40",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "악기제작학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 589},
            ],
        },
    ],
    "서울기독대": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천",
            "capacity": "1",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "53",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "복지·경영 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "농어촌출신자",
            "capacity": "1",
            "method": "학생부100",
            "csat_minimum": "없음",
            "notes": "유형 I만 인정",
            "source_refs": [
                {"section_id": "rural", "section_title": "농어촌학생 특별전형", "page": 278},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "기초생활수급자 및 차상위계층",
            "capacity": "3",
            "method": "학생부100",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {
                    "section_id": "low-income",
                    "section_title": "기초생활수급자·차상위계층·한부모가족지원대상자 특별전형",
                    "page": 296,
                },
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "특성화고교졸업자",
            "capacity": "1",
            "method": "학생부70+면접30",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {"section_id": "vocational", "section_title": "특성화고교졸업자 특별전형", "page": 303},
            ],
        },
    ],
    "감리교신학대": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "87",
            "method": "교과72+출결8+면접20",
            "csat_minimum": "없음",
            "notes": "신학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "추천자",
            "capacity": "25",
            "method": "교과72+출결8+면접20",
            "csat_minimum": "없음",
            "notes": "신학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 99},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "농어촌학생",
            "capacity": "4",
            "method": "학생부80+면접20",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {"section_id": "rural", "section_title": "농어촌학생 특별전형", "page": 271},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "기초생활수급권자 및 차상위계층",
            "capacity": "4",
            "method": "학생부80+면접20",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {
                    "section_id": "low-income",
                    "section_title": "기초생활수급자·차상위계층·한부모가족지원대상자 특별전형",
                    "page": 289,
                },
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "특수교육대상자",
            "capacity": "20",
            "method": "학생부80+면접20",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {"section_id": "disability", "section_title": "장애인 등 대상자 특별전형", "page": 313},
            ],
        },
    ],
    "경운대(구미)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과일반(인문·자연)",
            "capacity": "388",
            "method": "교과90+출결10",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 10 / 항공운항: 국,수,영,탐/직(1) 중 3개 합 10",
            "notes": "구미 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과면접",
            "capacity": "221",
            "method": "교과63+출결7+면접30",
            "csat_minimum": "없음",
            "notes": "구미 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재",
            "capacity": "35",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 10",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 350},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과일반(디자인융합학부)",
            "capacity": "13",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "디자인융합학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 594},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재(디자인융합학부)",
            "capacity": "5",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "디자인융합학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 594},
            ],
        },
    ],
    "청운대(홍성)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반(인문·자연)",
            "capacity": "223",
            "method": "교과78.7+출결21.3",
            "csat_minimum": "없음",
            "notes": "홍성 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "청운인재(인문)",
            "capacity": "53",
            "method": "교과44+출결12+면접44",
            "csat_minimum": "없음",
            "notes": "홍성 캠퍼스 인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재",
            "capacity": "26",
            "method": "교과78.7+출결21.3",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 344},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(공간디자인)",
            "capacity": "25",
            "method": "교과78.7+출결21.3",
            "csat_minimum": "없음",
            "notes": "공간디자인학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 593},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(방송영화영상)",
            "capacity": "25",
            "method": "교과78.7+출결21.3",
            "csat_minimum": "없음",
            "notes": "방송영화영상학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 593},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "청운인재-면접",
            "capacity": "25",
            "method": "교과44.1+출결11.9+면접44",
            "csat_minimum": "없음",
            "notes": "공연기획경영학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 593},
            ],
        },
    ],
    "동국대(고양)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교장추천인재",
            "capacity": "41",
            "method": "교과70+서류30",
            "csat_minimum": "없음",
            "notes": "고양 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 97},
            ],
        },
        {
            "admission_type": "논술",
            "track_name": "논술전형",
            "capacity": "5",
            "method": "논술70+교과20+출결10",
            "csat_minimum": "",
            "notes": "자연계 논술 모집 기준",
            "source_refs": [
                {"section_id": "regular-03", "section_title": "논술전형", "page": 198},
                {"section_id": "regular-03", "section_title": "논술전형", "page": 222},
            ],
        },
    ],
    "서울한영대": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "143",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "농어촌학생",
            "capacity": "3",
            "method": "학생부100",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {"section_id": "rural", "section_title": "농어촌학생 특별전형", "page": 278},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "기초생활수급자·차상위·한부모",
            "capacity": "5",
            "method": "학생부100",
            "csat_minimum": "없음",
            "notes": "기초생활수급자, 차상위계층, 한부모가족지원대상자 기준",
            "source_refs": [
                {
                    "section_id": "low-income",
                    "section_title": "기초생활수급자·차상위계층·한부모가족지원대상자 특별전형",
                    "page": 296,
                },
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "장애인등 대상자",
            "capacity": "18",
            "method": "학생부60+면접40",
            "csat_minimum": "없음",
            "notes": "교과 특별전형",
            "source_refs": [
                {"section_id": "disability", "section_title": "장애인 등 대상자 특별전형", "page": 319},
            ],
        },
    ],
    "총신대": [
        {
            "admission_type": "학생부종합",
            "track_name": "목회자추천자",
            "capacity": "22",
            "method": "서류70+면접30",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "코람데오인재",
            "capacity": "120",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 168},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "기초생활수급자 및 차상위계층",
            "capacity": "16",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "종합 특별전형",
            "source_refs": [
                {
                    "section_id": "low-income",
                    "section_title": "기초생활수급자·차상위계층·한부모가족지원대상자 특별전형",
                    "page": 296,
                },
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "특수교육대상자",
            "capacity": "20",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "종합 특별전형",
            "source_refs": [
                {"section_id": "disability", "section_title": "장애인 등 대상자 특별전형", "page": 319},
            ],
        },
    ],
    "한양대(ERICA)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역균형선발",
            "capacity": "509",
            "method": "교과100",
            "csat_minimum": "있음",
            "notes": "2027학년도 지역균형전형 표 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 146},
            ],
        },
    ],
    "광주여대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생Ⅰ(간호·물리치료)",
            "capacity": "84",
            "method": "교과58.2+출결11.9+면접29.9",
            "csat_minimum": "없음",
            "notes": "간호·물리치료 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생Ⅰ(항공서비스)",
            "capacity": "40",
            "method": "교과50.6+출결10.4+면접39",
            "csat_minimum": "없음",
            "notes": "항공서비스학과 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생Ⅱ(인문·자연)",
            "capacity": "410",
            "method": "교과83+출결17",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재",
            "capacity": "36",
            "method": "교과83+출결17",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 330},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생Ⅰ(스포츠)",
            "capacity": "15",
            "method": "교과58.2+출결11.9+면접29.9",
            "csat_minimum": "없음",
            "notes": "스포츠학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생Ⅱ(스포츠)",
            "capacity": "5",
            "method": "교과83+출결17",
            "csat_minimum": "없음",
            "notes": "스포츠학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
    ],
    "남부대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(간호 등)",
            "capacity": "446",
            "method": "교과90+출결10",
            "csat_minimum": "간호: 국,수,영,탐(1) 중 2개 합 12",
            "notes": "간호 등 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(IT경영 등)",
            "capacity": "52",
            "method": "교과63+출결7+면접30",
            "csat_minimum": "없음",
            "notes": "IT경영 등 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재(면접형)",
            "capacity": "20",
            "method": "교과63+출결7+면접30",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 332},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재(교과형)",
            "capacity": "9",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 332},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재기회균형",
            "capacity": "2",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 332},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(무도경호)",
            "capacity": "30",
            "method": "교과63+출결7+면접30",
            "csat_minimum": "없음",
            "notes": "무도경호학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(스포츠레저)",
            "capacity": "38",
            "method": "교과63+출결7+면접30",
            "csat_minimum": "없음",
            "notes": "스포츠레저학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
    ],
    "호남대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생A(인문·자연)",
            "capacity": "104",
            "method": "교과50+출결10+면접40",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생A(간호)",
            "capacity": "78",
            "method": "1단계(3배수): 교과83+출결17 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "간호학과 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생A(물리치료)",
            "capacity": "18",
            "method": "1단계(5배수): 교과83+출결17 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "물리치료학과 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생B(인문·자연)",
            "capacity": "474",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반고",
            "capacity": "389",
            "method": "교과80+출결20",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 평균 5 / 물리치료: 국,수,영,탐/직(1) 중 2개 평균 6(수 포함)",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재",
            "capacity": "126",
            "method": "교과80+출결20",
            "csat_minimum": "물리치료: 국,수,영,탐/직(1) 중 2개 평균 6",
            "notes": "지역인재 표 원문에서 물리치료 기준은 확인됨, 간호 기준은 줄바꿈으로 추가 확인 필요",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 336},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생A(e스포츠산업)",
            "capacity": "29",
            "method": "교과49.8+출결10.2+면접40",
            "csat_minimum": "없음",
            "notes": "e스포츠산업학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생A(스포츠레저)",
            "capacity": "37",
            "method": "교과49.8+출결10.2+면접40",
            "csat_minimum": "없음",
            "notes": "스포츠레저학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
    ],
    "경동대(양주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(인문·자연)",
            "capacity": "564",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "양주 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 103},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(스포츠마케팅)",
            "capacity": "49",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "스포츠마케팅학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 598},
            ],
        },
    ],
    "경북대(상주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자(건강운동관리)",
            "capacity": "10",
            "method": "교과80+서류20",
            "csat_minimum": "없음",
            "notes": "체육학부 건강운동관리전공 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 600},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자(체육학)",
            "capacity": "4",
            "method": "교과80+서류20",
            "csat_minimum": "없음",
            "notes": "체육학부 체육학전공 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 600},
            ],
        },
    ],
    "국립경국대(안동)": [
        {
            "admission_type": "학생부종합",
            "track_name": "바른인재",
            "capacity": "238",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "간호학부는 1단계(4배수): 서류100 / 2단계: 1단계70+면접30",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 179},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "선수출신자",
            "capacity": "4",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "체육학전공 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 601},
            ],
        },
    ],
    "김천대(김천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반면접",
            "capacity": "10",
            "method": "교과52.9+출결11.8+면접35.3",
            "csat_minimum": "없음",
            "notes": "생활체육학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 601},
            ],
        },
    ],
    "동명대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반고교과(인문·자연)",
            "capacity": "399",
            "method": "교과100",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 9",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접(인문·자연)",
            "capacity": "220",
            "method": "교과78.3+면접21.7",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 9",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재",
            "capacity": "13",
            "method": "학생부75.9+서류24.1",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 330},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접(스포츠재활학과)",
            "capacity": "2",
            "method": "교과78.3+면접21.7",
            "csat_minimum": "없음",
            "notes": "스포츠재활학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 601},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반고교과(스포츠재활학과)",
            "capacity": "3",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "스포츠재활학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 601},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재(스포츠재활학과)",
            "capacity": "2",
            "method": "교과75.9+서류24.1",
            "csat_minimum": "없음",
            "notes": "스포츠재활학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 601},
            ],
        },
    ],
    "목원대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과면접(유아교육)",
            "capacity": "17",
            "method": "교과80+면접20",
            "csat_minimum": "없음",
            "notes": "유아교육과 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과(인문·자연)",
            "capacity": "1032",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재",
            "capacity": "138",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 334},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과(스포츠건강관리)",
            "capacity": "20",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "스포츠건강관리학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 599},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재(스포츠건강관리)",
            "capacity": "3",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "스포츠건강관리학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 599},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과(연극영화영상학부)",
            "capacity": "25",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "연극영화영상학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 604},
            ],
        },
    ],
    "배재대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과(인문·자연)",
            "capacity": "907",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반고교과(인문·자연)",
            "capacity": "319",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "대전 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "항공인재",
            "capacity": "10",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "항공서비스 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재Ⅰ",
            "capacity": "88",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 334},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재Ⅱ",
            "capacity": "3",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 334},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과(스포츠마케팅)",
            "capacity": "25",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "레저스포츠학부 스포츠마케팅 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 599},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반고교과(스포츠지도·건강재활)",
            "capacity": "10",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "레저스포츠학부 스포츠지도·건강재활 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 599},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재I(스포츠지도·건강재활)",
            "capacity": "5",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "레저스포츠학부 스포츠지도·건강재활 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 599},
            ],
        },
    ],
    "부산외국어대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과면접",
            "capacity": "5",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "사회체육전공(자유전공) 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 601},
            ],
        },
    ],
    "세명대(제천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반(인문·자연)",
            "capacity": "657",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "제천 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "인문계고교(인문·자연)",
            "capacity": "187",
            "method": "교과100",
            "csat_minimum": "한의예: 국,수,영,탐(1) 중 3개 합 5 (수 포함)",
            "notes": "제천 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접우수자",
            "capacity": "93",
            "method": "교과50.5+면접49.5",
            "csat_minimum": "없음",
            "notes": "제천 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재(일반)",
            "capacity": "97",
            "method": "교과100",
            "csat_minimum": "한의예",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 338},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재(기회균형)",
            "capacity": "4",
            "method": "교과100",
            "csat_minimum": "한의예",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 338},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "인문계고교(시각·영상디자인)",
            "capacity": "14",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "시각·영상디자인학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 593},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(실내디자인)",
            "capacity": "20",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "실내디자인학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 594},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재(일반·연기예술)",
            "capacity": "2",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "연기예술학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 604},
            ],
        },
    ],
    "동양대(영주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반Ⅰ",
            "capacity": "38",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "디지털콘텐츠학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 607},
            ],
        },
    ],
    "대신대(경산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "21",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "문화예술학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 609},
            ],
        },
    ],
    "전주대(전주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "17",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "산업디자인학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 596},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재1",
            "capacity": "76",
            "method": "학생부100",
            "csat_minimum": "없음",
            "notes": "전공자율선택제 경영대학 유형2 기준",
            "source_refs": [
                {"section_id": "major-free-choice", "section_title": "전공자율선택제", "page": 386},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반학생",
            "capacity": "75",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "전공자율선택제 경영대학 유형2 기준",
            "source_refs": [
                {"section_id": "major-free-choice", "section_title": "전공자율선택제", "page": 386},
            ],
        },
    ],
    "신라대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반고교과(인문·자연)",
            "capacity": "527",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접우수자(인문·자연)",
            "capacity": "290",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "부산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "미래인재",
            "capacity": "40",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "미래융합 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재",
            "capacity": "20",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 344},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접우수자(체육학부)",
            "capacity": "6",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "체육학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 601},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반고교과(체육학부)",
            "capacity": "8",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "체육학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 601},
            ],
        },
    ],
    "영산대(해운대)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반계고",
            "capacity": "70",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "해운대 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과(인문·자연)",
            "capacity": "73",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "해운대 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "항공관광",
            "capacity": "25",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "해운대 캠퍼스 항공관광 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과(레저스포츠관광)",
            "capacity": "2",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "레저스포츠관광학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접(레저스포츠관광)",
            "capacity": "6",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "레저스포츠관광학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "일반전형",
            "capacity": "2",
            "method": "수능70+교과30",
            "csat_minimum": "",
            "notes": "연기공연미디어학부 연기공연예술전공 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 632},
            ],
        },
    ],
    "영산대(양산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반계고",
            "capacity": "257",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "양산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 111},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과(인문·자연)",
            "capacity": "180",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "양산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 111},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접(인문·자연)",
            "capacity": "53",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "양산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 111},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과(동양무예)",
            "capacity": "7",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "동양무예학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접(동양무예)",
            "capacity": "22",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "동양무예학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
    ],
    "송원대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부우수자(인문·자연)",
            "capacity": "309",
            "method": "교과75+출결25",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접우수자(간호)",
            "capacity": "128",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "간호학과 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접우수자-면접",
            "capacity": "8",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "스포츠데이터분석학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부우수자-일반",
            "capacity": "4",
            "method": "교과75+출결25",
            "csat_minimum": "없음",
            "notes": "스포츠지도학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
    ],
    "세한대(영암)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "50",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "스포츠융합복지학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 610},
            ],
        },
    ],
    "안양대(강화)": [
        {
            "admission_type": "학생부교과",
            "track_name": "아리학생부교과",
            "capacity": "11",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "게임콘텐츠학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 606},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "아리학생부면접",
            "capacity": "5",
            "method": "1단계(6배수): 교과100 / 2단계: 1단계60+면접40",
            "csat_minimum": "없음",
            "notes": "게임콘텐츠학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 606},
            ],
        },
    ],
    "루터대(용인)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "45",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "정시",
            "track_name": "일반",
            "capacity": "26",
            "method": "수능60+학생부40",
            "csat_minimum": "",
            "notes": "전공자율선택제 휴먼케어서비스학부 기준",
            "source_refs": [
                {"section_id": "major-free-choice", "section_title": "전공자율선택제", "page": 543},
            ],
        },
    ],
    "서울장신대(경기 광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "42",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
    ],
    "수원가톨릭대(화성)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "1",
            "method": "1단계(2배수): 교과80+출결10+봉사10 / 2단계: 1단계60+면접40",
            "csat_minimum": "국,수,영,탐,한 5개 각 2",
            "notes": "신학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
    ],
    "부산장신대(김해)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "20",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "특수교육 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "추천제",
            "capacity": "12",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "신학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
    ],
    "목포가톨릭대(목포)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "73",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 116},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재",
            "capacity": "31",
            "method": "서류60+학생부40",
            "csat_minimum": "없음",
            "notes": "지역인재 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 374},
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 221},
            ],
        },
    ],
    "광신대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "3",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
    ],
    "광주가톨릭대(나주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부A",
            "capacity": "13",
            "method": "교과54+출결6+면접20+교리20",
            "csat_minimum": "없음",
            "notes": "신학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 115},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부B",
            "capacity": "9",
            "method": "교과54+출결6+면접20+교리20",
            "csat_minimum": "국,수,영,탐/직(절사),한 5개 합 25",
            "notes": "신학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 115},
            ],
        },
    ],
    "대전가톨릭대(세종)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "1",
            "method": "교과60+면접20+기타20",
            "csat_minimum": "국,수,영,탐 4개 합 6, 한 3",
            "notes": "신학 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
    ],
    "아신대(양평)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "90",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 102},
            ],
        },
    ],
    "가야대(김해)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "199",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "가야인재",
            "capacity": "151",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "간호·물리치료 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재",
            "capacity": "18",
            "method": "교과100",
            "csat_minimum": "",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 369},
            ],
        },
    ],
    "가톨릭꽃동네대(청주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "33",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "자율·간호 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 127},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "휴먼리더면접",
            "capacity": "10",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "간호 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 127},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재",
            "capacity": "18",
            "method": "교과60+면접40",
            "csat_minimum": "",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 369},
            ],
        },
    ],
    "건양대(논산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반(교과)",
            "capacity": "431",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "군사학",
            "capacity": "35",
            "method": "1단계(5배수): 교과100 / 2단계: 1단계27.2+면접48.5+체력24.3",
            "csat_minimum": "없음",
            "notes": "군사 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
    ],
    "국립금오공과대(구미)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과",
            "capacity": "447",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 9",
            "notes": "인문·자연 기준, 자연계열은 수(미/기) 반영 시 1등급 상향, 스마트모빌리티전공은 수 포함",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "KIT인재",
            "capacity": "229",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "자율인재",
            "capacity": "60",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 181},
            ],
        },
    ],
    "국립목포해양대(목포)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부성적우수자",
            "capacity": "322",
            "method": "교과90+출결10",
            "csat_minimum": "항해: 국,수,영,탐(1) 중 2개 합 9 / 해상운송·항해정보·해군사관: 국,수,영,탐(1) 중 2개 합 10",
            "notes": "자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "누구나",
            "capacity": "87",
            "method": "교과90+출결10",
            "csat_minimum": "",
            "notes": "자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 113},
            ],
        },
    ],
    "국립한국교통대(의왕)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "31",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "의왕 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 98},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합전형Ⅱ",
            "capacity": "106",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "의왕 캠퍼스 학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 162},
            ],
        },
    ],
    "국립한국해양대(부산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "86",
            "method": "교과100",
            "csat_minimum": "해사대학: 수,영,탐(절사) 중 2개 합 9 / 해양과학기술융합대학: 수,영,탐(절사) 중 1개 5 / 해양인문사회과학대학: 국,영,탐(절사) 중 2개 합 9",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수자",
            "capacity": "757",
            "method": "교과100",
            "csat_minimum": "",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "아치해양인재전형Ⅰ",
            "capacity": "99",
            "method": "서류40+학생부60",
            "csat_minimum": "있음",
            "notes": "학생부종합전형 표 수능최저 유무 ○",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 192},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "아치해양인재전형Ⅱ",
            "capacity": "38",
            "method": "서류100",
            "csat_minimum": "있음",
            "notes": "학생부종합전형 표 수능최저 유무 ○",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 192},
            ],
        },
    ],
    "국립한밭대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "1,004",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 103},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재",
            "capacity": "141",
            "method": "교과90+출결10",
            "csat_minimum": "",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 346},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합(학석사)",
            "capacity": "92",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합(일반)",
            "capacity": "238",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역인재(종합)",
            "capacity": "138",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
                {"section_id": "regional", "section_title": "지역인재전형", "page": 346},
            ],
        },
    ],
    "극동대(음성)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "364",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "187",
            "method": "교과54+출결6+면접40",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
    ],
    "금강대(논산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "78",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "프라마나 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "금강인재추천",
            "capacity": "20",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "프라마나 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
    ],
    "세한대(당진)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "116",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "항공서비스 등",
            "capacity": "60",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "항공서비스 등 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
    ],
    "중부대(고양)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교생활우수자",
            "capacity": "144",
            "method": "교과65.1+면접34.9",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "항공서비스",
            "capacity": "60",
            "method": "교과51+면접49",
            "csat_minimum": "없음",
            "notes": "항공서비스 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부우수자",
            "capacity": "649",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
    ],
    "중부대(금산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학교생활우수자",
            "capacity": "80",
            "method": "교과65.1+면접34.9",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부우수자",
            "capacity": "252",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
    ],
    "창신대(창원)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반계고교",
            "capacity": "272",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "창신인재면접",
            "capacity": "127",
            "method": "교과54+출결6+면접40",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 114},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재",
            "capacity": "4",
            "method": "교과90+출결10",
            "csat_minimum": "",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 347},
            ],
        },
    ],
    "청운대(인천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "276",
            "method": "교과78.7+출결21.3",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 98},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "청운인재",
            "capacity": "41",
            "method": "교과44+출결12+면접44",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 98},
            ],
        },
    ],
    "초당대(무안)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반고",
            "capacity": "90",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "간호·항공운항 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 116},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "340",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 116},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "항공관광서비스",
            "capacity": "20",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "항공관광서비스 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 116},
            ],
        },
    ],
    "제주국제대(제주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "대학독자",
            "capacity": "13",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 117},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "177",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 117},
            ],
        },
    ],
    "협성대(화성)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과성적우수자",
            "capacity": "299",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "미래창의인재",
            "capacity": "93",
            "method": "1단계(7배수): 교과100 / 2단계: 1단계50+면접50",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "융합인재Ⅰ서류",
            "capacity": "112",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 156},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "융합인재Ⅱ면접",
            "capacity": "103",
            "method": "1단계(4배수): 서류100 / 2단계: 면접50+1단계50",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 156},
            ],
        },
    ],
    "화성의과학대(화성)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "195",
            "method": "교과100",
            "csat_minimum": "간호: 국,수,영 중 2개 합 10",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 101},
            ],
        },
    ],
    "호서대(아산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부",
            "capacity": "408",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "아산 캠퍼스 인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접",
            "capacity": "44",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "아산 캠퍼스 인문 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "호서인재",
            "capacity": "240",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "아산 캠퍼스 학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
    ],
    "한동대(포항)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "60",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 7 또는 1개 1",
            "notes": "전 모집단위 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "한동인재",
            "capacity": "110",
            "method": "교과70+서류30",
            "csat_minimum": "없음",
            "notes": "전 모집단위 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "G-IMPACT인재",
            "capacity": "213",
            "method": "1단계(2.5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 179},
            ],
        },
    ],
    "한일장신대(완주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "57",
            "method": "교과80+면접20",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 117},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "간호",
            "capacity": "51",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "간호 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 117},
            ],
        },
    ],
    "포항공과대(포항)": [
        {
            "admission_type": "학생부종합",
            "track_name": "일반Ⅰ",
            "capacity": "220",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계50+면접50",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 179},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반Ⅱ",
            "capacity": "70",
            "method": "1단계(3배수): 서류100 / 2단계: 1단계67+면접33",
            "csat_minimum": "있음",
            "notes": "학생부종합전형 표 수능최저 유무 ○",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 179},
            ],
        },
    ],
    "홍익대(세종)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과우수자",
            "capacity": "315",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 1개 4",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학교생활우수자",
            "capacity": "199",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "세종 캠퍼스 학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 167},
            ],
        },
    ],
    "칼빈대(용인)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(인문·자연)",
            "capacity": "52",
            "method": "교과55+면접45",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 100},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생(스포츠지도)",
            "capacity": "23",
            "method": "교과55+면접45",
            "csat_minimum": "없음",
            "notes": "스포츠지도학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 580},
            ],
        },
    ],
    "한국침례신학대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "기독교인",
            "capacity": "4",
            "method": "교과80+면접20",
            "csat_minimum": "",
            "notes": "음악학부 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 548},
            ],
        },
    ],
    "호남신학대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "17",
            "method": "교과45.71+출결·봉사11.43+면접42.86",
            "csat_minimum": "없음",
            "notes": "기독사회복지상담 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 116},
            ],
        },
    ],
    "예수대(전주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반학생",
            "capacity": "50",
            "method": "교과90+출결10",
            "csat_minimum": "국,수,영,탐(1) 중 2개 합 10",
            "notes": "간호 기준, 수(미/기) 포함 시 2개 합 11",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 117},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재",
            "capacity": "47",
            "method": "교과90+출결10",
            "csat_minimum": "국,수(확),영,탐(1) 중 2개 합 10",
            "notes": "간호 기준, 수(미/기) 선택 시 11",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 353},
            ],
        },
    ],
    "우석대(진천)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과(인문·자연)",
            "capacity": "215",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과면접",
            "capacity": "20",
            "method": "1단계(5배수): 교과100 / 2단계: 교과70+면접30",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "교과(생활체육)",
            "capacity": "1",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "생활체육학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 599},
            ],
        },
    ],
    "위덕대(경주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "184",
            "method": "교과80+출결20",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접",
            "capacity": "112",
            "method": "교과51+면접49",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재 특별",
            "capacity": "35",
            "method": "교과51+면접49",
            "csat_minimum": "",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 352},
            ],
        },
    ],
    "유원대(아산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "유원교과",
            "capacity": "292",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "유원면접",
            "capacity": "87",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 109},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합",
            "capacity": "3",
            "method": "학생부60+면접40",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 171},
            ],
        },
    ],
    "유원대(영동)": [
        {
            "admission_type": "학생부교과",
            "track_name": "유원교과",
            "capacity": "227",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "유원면접",
            "capacity": "116",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 110},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재Ⅰ",
            "capacity": "30",
            "method": "교과60+면접40",
            "csat_minimum": "",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 345},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합",
            "capacity": "17",
            "method": "학생부60+면접40",
            "csat_minimum": "없음",
            "notes": "학생부종합전형 표 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 172},
            ],
        },
    ],
    "을지대(대전)": [
        {
            "admission_type": "학생부교과",
            "track_name": "지역의료인재(일반형)",
            "capacity": "62",
            "method": "교과100",
            "csat_minimum": "",
            "notes": "의예 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 345},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역의료인재(특별형)",
            "capacity": "3",
            "method": "서류100",
            "csat_minimum": "",
            "notes": "의예 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 345},
            ],
        },
    ],
    "전주교대(전주)": [
        {
            "admission_type": "정시",
            "track_name": "일반학생",
            "capacity": "79",
            "method": "1단계(2배수): 수능100 / 2단계: 1단계90+면접10",
            "csat_minimum": "",
            "notes": "백분위 반영",
            "source_refs": [
                {"section_id": "education", "section_title": "교육대학 전형", "page": 483},
            ],
        },
    ],
    "한서대(서산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과(인문·자연)",
            "capacity": "508",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "서산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 103},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "항공관광",
            "capacity": "30",
            "method": "교과54+출결6+면접40",
            "csat_minimum": "없음",
            "notes": "항공관광 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 103},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "한서인재",
            "capacity": "187",
            "method": "교과54+출결6+면접40",
            "csat_minimum": "없음",
            "notes": "서산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 103},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과(영화영상)",
            "capacity": "15",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "영화영상학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 604},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "학생부교과(예체능전공자율)",
            "capacity": "20",
            "method": "교과90+출결10",
            "csat_minimum": "없음",
            "notes": "예체능전공자율학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 609},
            ],
        },
    ],
    "서원대(청주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "인문계고",
            "capacity": "185",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "청주 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(인문·자연)",
            "capacity": "672",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "청주 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "사범대",
            "capacity": "182",
            "method": "교과80+면접20",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 8 / 유아교육: 국,수,영,탐/직(1) 중 2개 합 9",
            "notes": "사범대 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재",
            "capacity": "45",
            "method": "교과100",
            "csat_minimum": "사범: 국,수,영,탐/직(1) 중 2개 합 9 / 수학교육: 확률과 통계 3 또는 미적분·기하 4 이내",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 338},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(디자인학과)",
            "capacity": "10",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "디자인학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 593},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "창의면접",
            "capacity": "5",
            "method": "교과55+면접45",
            "csat_minimum": "없음",
            "notes": "웹툰콘텐츠학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 593},
            ],
        },
    ],
    "청주대(청주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과면접",
            "capacity": "3",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "공예디자인학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 594},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "5",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "아트앤패션디자인학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 594},
            ],
        },
    ],
    "선문대(아산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반(인문·자연)",
            "capacity": "1089",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "아산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "면접",
            "capacity": "111",
            "method": "교과60+면접40",
            "csat_minimum": "없음",
            "notes": "아산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 104},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역학생",
            "capacity": "270",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 338},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역저소득층",
            "capacity": "2",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 338},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(영화영상학과)",
            "capacity": "32",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "영화영상학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 604},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "지역인재(영화영상학과)",
            "capacity": "4",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "영화영상학과 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 604},
            ],
        },
    ],
    "호원대(군산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반(인문·자연)",
            "capacity": "214",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "군산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "간호",
            "capacity": "60",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "간호학과 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재(기초)",
            "capacity": "35",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 595},
            ],
        },
        {
            "admission_type": "지역인재",
            "track_name": "지역인재(기초생활수급자 등)",
            "capacity": "3",
            "method": "교과70+면접30",
            "csat_minimum": "없음",
            "notes": "지역인재전형 표 기준",
            "source_refs": [
                {"section_id": "regional", "section_title": "지역인재전형", "page": 595},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "일반(스포츠무도)",
            "capacity": "26",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "스포츠무도학과[야] 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 602},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "성인학습자",
            "capacity": "20",
            "method": "교과100",
            "csat_minimum": "없음",
            "notes": "K-콘텐츠제작학과[야] 기준",
            "source_refs": [
                {"section_id": "arts-sports", "section_title": "예체능계열", "page": 603},
            ],
        },
    ],
    "국립한국교통대(충주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "729",
            "method": "교과100",
            "csat_minimum": "",
            "notes": "충주 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 105},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합Ⅰ",
            "capacity": "21",
            "method": "1단계(7배수): 서류100 / 2단계: 서류60+면접40",
            "csat_minimum": "없음",
            "notes": "충주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 177},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "학생부종합Ⅱ",
            "capacity": "367",
            "method": "서류100",
            "csat_minimum": "없음",
            "notes": "충주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 177},
            ],
        },
    ],
    "계명대(대구)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "792",
            "method": "교과80+출결20",
            "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 9~10",
            "notes": "경찰행정·간호 2개 합 7, 기독교·철학·사진영상미디어·경영(야) 없음",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "의예",
            "capacity": "9",
            "method": "1단계(20배수): 교과80+출결20 / 2단계: 1단계70+면접30",
            "csat_minimum": "국,수(미/기),영,과(1) 중 3개 합 3",
            "notes": "수(미/기), 과(2) 필수 응시",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 106},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "일반",
            "capacity": "907",
            "method": "서류100 / 의예 일부 1단계(10배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "의/약 일부 적용",
            "notes": "대구 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 178},
            ],
        },
    ],
    "대구가톨릭대(경산)": [
        {
            "admission_type": "학생부교과",
            "track_name": "교과",
            "capacity": "1,050",
            "method": "교과80+출결20",
            "csat_minimum": "약학: 국,수(미/기),영,과(절사) 중 3개 합 5 / 간호: 국,수,영,탐/직(1) 중 2개 합 7",
            "notes": "경산 캠퍼스 인문·자연 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 107},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "의예·신학",
            "capacity": "28",
            "method": "1단계(5배수): 교과80+출결20 / 2단계: 1단계80+면접20",
            "csat_minimum": "의예: 국,수(미/기),영,과(절사) 중 3개 합 4",
            "notes": "의예는 1단계 7배수",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 107},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "종합",
            "capacity": "354",
            "method": "서류100 / 일부 모집단위 1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 8",
            "notes": "글로벌항공서비스는 1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 179},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "지역종합",
            "capacity": "66",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 5(수(미/기), 과 응시 필수) / 약학: 국,수(미/기),영,과 중 3개 합 6(수(미/기), 과 응시 필수)",
            "notes": "의예·약학은 1단계(7배수): 서류100 / 2단계: 1단계80+면접20",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 179},
                {"section_id": "regional", "section_title": "지역인재전형", "page": 3422},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "SW",
            "capacity": "18",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
            "csat_minimum": "없음",
            "notes": "",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 179},
            ],
        },
    ],
    "조선대(광주)": [
        {
            "admission_type": "학생부교과",
            "track_name": "일반",
            "capacity": "1,362",
            "method": "교과100",
            "csat_minimum": "국,수,영,탐(1) 중 1개 6",
            "notes": "간호 2개 합 6, 사범대 2개 합 10, 약학 3개 합 6, 의예·치의예 3개 합 5",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부교과",
            "track_name": "군사학과",
            "capacity": "30",
            "method": "1단계(5배수): 교과100 / 2단계: 1단계18.9+면접54.1+체력27",
            "csat_minimum": "없음",
            "notes": "군사학과 기준",
            "source_refs": [
                {"section_id": "regular-01", "section_title": "학생부교과전형", "page": 112},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "면접",
            "capacity": "248",
            "method": "1단계(5배수): 서류100 / 2단계: 1단계70+면접30",
            "csat_minimum": "의/치/약 일부 적용",
            "notes": "광주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 183},
            ],
        },
        {
            "admission_type": "학생부종합",
            "track_name": "서류",
            "capacity": "1,127",
            "method": "서류100",
            "csat_minimum": "의/치/약 일부 적용",
            "notes": "광주 캠퍼스 기준",
            "source_refs": [
                {"section_id": "regular-02", "section_title": "학생부종합전형", "page": 183},
            ],
        },
    ],
}

CSAT_MINIMUM_OVERRIDES = {
    ("가톨릭대(성심)", "학생부교과", "지역균형"): {
        "csat_minimum": "인문·자연: 국,수,영,탐(1) 중 2개 합 7 / 자유전공·인문사회계열·자연공학계열: 2개 합 6 / 약학: 국,수,영,과(1) 중 3개 합 5",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("강남대(용인)", "학생부교과", "지역균형"): {
        "csat_minimum": "주간: 국,수,영,탐(1) 중 1개 3 / 야간: 없음",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("경북대(대구)", "학생부종합", "일반학생"): {
        "csat_minimum": "인문·사회과학·자연과학·농업생명과학·생활과학: 국,수,영,탐(1) 중 2개 합 7 / 공과·첨단기술융합·공학첨단자율·IT: 2개 합 6~7(수 포함) / 경상·사범·간호·행정·자율전공: 2개 합 6 / 수의예: 3개 합 5(수 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("경북대(대구)", "학생부종합", "지역인재"): {
        "csat_minimum": "의예·치의예: 국,수,영,탐 중 3개 합 4(수 포함) / 약학: 국,수,영,탐 중 3개 합 5(수 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("경북대(대구)", "학생부종합", "지역인재 학교장추천"): {
        "csat_minimum": "의예·치의예: 국,수,영,탐 중 3개 합 4(수 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("경인교대(인천)", "학생부교과", "학교장추천"): {
        "csat_minimum": "국,수,영,탐(1) 4개 합 14",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("경희대", "학생부종합", "네오르네상스"): {
        "csat_minimum": "의예·치의예·한의예·약학: 국,수,영,탐 중 3개 합 4, 한 5",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("계명대(대구)", "학생부종합", "일반"): {
        "csat_minimum": "의예: 국,수(미/기),영,과(1) 중 3개 합 4(수 포함, 수(미/기)·과 응시 필수) / 약학: 국,수(미/기),영,과(1) 중 3개 합 6(수(미/기)·과 응시 필수)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("고려대(세종)", "논술", "약학"): {
        "csat_minimum": "약학: 국,수(미/기),영,과 중 3개 합 5",
        "notes": "의약학계열 논술전형 수능최저 상세표 기준",
    },
    ("국립강릉원주대(강릉)", "학생부종합", "해람인재"): {
        "csat_minimum": "치의예: 국,수,영,과(1) 중 3개 합 6(수 포함)",
        "notes": "의약학계열 학생부종합전형 수능최저 상세표 기준",
    },
    ("국립목포대(목포)", "학생부종합", "지역인재"): {
        "csat_minimum": "약학: 국,수(미/기),영,과 중 3개 합 7(수(미/기), 과 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("국립순천대(순천)", "학생부종합", "종합면접"): {
        "csat_minimum": "약학: 국,수(미/기),영,과 중 3개 합 7(수(미/기), 과 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("국립한국해양대(부산)", "학생부종합", "아치해양인재전형Ⅰ"): {
        "csat_minimum": "해사대학: 수,영,탐 중 2개 합 9 / 해양과학기술융합: 수,영,탐 중 1개 5 / 해양인문사회과학: 국,영,탐 중 2개 합 9",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("국립한국해양대(부산)", "학생부종합", "아치해양인재전형Ⅱ"): {
        "csat_minimum": "해사대학: 국,영,탐 중 2개 합 9 / 해양과학기술융합: 수,영,탐 중 1개 5 / 해양인문사회과학: 국,영,탐 중 2개 합 9",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("단국대(죽전)", "학생부교과", "지역균형선발"): {
        "csat_minimum": "국,수,영,탐(1) 중 2개 합 6",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("단국대(천안)", "학생부종합", "DKU인재-면접형"): {
        "csat_minimum": "의예·치의예: 국,수(미/기),영,과 중 3개 합 5(수 포함) / 약학: 국,수(미/기),영,과 중 3개 합 6(수 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("대구가톨릭대(경산)", "학생부종합", "종합"): {
        "csat_minimum": "간호: 국,수,영,탐/직(1) 중 2개 합 8",
        "notes": "글로벌항공서비스는 1단계(5배수): 서류100 / 2단계: 1단계80+면접20",
    },
    ("대구가톨릭대(경산)", "학생부종합", "지역종합"): {
        "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 5(수(미/기), 과 응시 필수) / 약학: 국,수(미/기),영,과 중 3개 합 6(수(미/기), 과 응시 필수)",
        "notes": "의예·약학은 1단계(7배수): 서류100 / 2단계: 1단계80+면접20",
    },
    ("덕성여대", "학생부교과", "고교추천"): {
        "csat_minimum": "국,수,영,탐(1) 중 2개 합 7 / 약학: 국,수,영,탐(1) 중 3개 합 5(수 포함, 영·사(1) 중 상위 1개만 적용)",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("동덕여대", "학생부교과", "학생부교과우수자"): {
        "csat_minimum": "국,수,영,탐(1) 중 2개 합 6 / 약학: 국,수(미/기),과(1) 3개 합 6",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("동덕여대", "학생부종합", "동덕창의리더"): {
        "csat_minimum": "약학: 국,수(미/기),과(1) 중 3개 합 6",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("동아대(부산)", "학생부종합", "잠재능력우수자"): {
        "csat_minimum": "의예: 국,수,영,탐 중 3개 합 4",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("부산대(부산)", "학생부종합", "지역인재"): {
        "csat_minimum": "의예: 국,수,영,탐 중 3개 합 4, 한 4(탐 응시 필수, 수 포함) / 치의예: 3개 합 5, 한 4(탐 응시 필수, 수 포함) / 약학: 국,수,영,탐(1) 중 3개 합 5, 한 4(탐 응시 필수, 수 포함) / 간호: 국,수,영,탐(1) 중 2개 합 6, 한 4(탐(2) 응시 필수, 수 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("부산대(부산)", "논술", "약학"): {
        "csat_minimum": "약학: 국,수,영,탐(1) 중 3개 합 4, 한 4",
        "notes": "의약학계열 논술전형 수능최저 상세표 기준",
    },
    ("삼육대", "학생부교과", "학교장추천"): {
        "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 7 / 간호·물리치료: 2개 합 6 / 약학: 국,수(미/기),영,과(1) 중 3개 합 5",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("삼육대", "학생부종합", "세움인재"): {
        "csat_minimum": "약학: 국,수(미/기),영,과(1) 중 3개 합 5",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("서울과학기술대", "학생부교과", "고교추천"): {
        "csat_minimum": "국,수,영,탐/직(1) 중 2개 합 7",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("서울교대", "학생부교과", "학교장추천"): {
        "csat_minimum": "국,수,영,탐 2개 합 6, 한 4",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("서울교대", "학생부종합", "교직인성우수자"): {
        "csat_minimum": "초등교육: 국,수,영,탐 중 2개 합 6, 한 4",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("서울여대", "학생부교과", "교과우수자"): {
        "csat_minimum": "국,수,영,탐(1) 중 2개 합 7",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("성균관대(수원)", "학생부종합", "서류형(융합인재)"): {
        "csat_minimum": "전 모집단위: 국,수,영,탐 중 3개 합 6",
        "notes": "과(1)/탐(2) 평균 중 우수등급 반영(의예 제외), 제2외국어 탐(1) 대체 가능",
    },
    ("성신여대", "학생부교과", "지역균형"): {
        "csat_minimum": "국,수,영,탐(1) 중 2개 합 7",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("수원대(화성)", "학생부교과", "고교추천"): {
        "csat_minimum": "국,수,영,탐/직(1) 중 1개 4",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("아주대(수원)", "학생부종합", "ACE"): {
        "csat_minimum": "의학: 국,수,영,탐 중 4개 합 6 / 약학: 국,수,영,탐 중 3개 합 5",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("울산대(울산)", "학생부종합", "잠재역량"): {
        "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 4, 한 4",
        "notes": "동일분야 I+II 불가",
    },
    ("울산대(울산)", "지역인재", "지역인재"): {
        "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 4, 한 4",
        "notes": "동일분야 I+II 불가",
    },
    ("울산대(울산)", "지역인재", "지역인재 특별(기초생활수급자 등)"): {
        "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 4, 한 4",
        "notes": "동일분야 I+II 불가",
    },
    ("울산대(울산)", "학생부종합", "지역인재"): {
        "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 4, 한 4",
        "notes": "동일분야 I+II 불가",
    },
    ("을지대(성남)", "학생부교과", "지역균형"): {
        "csat_minimum": "간호: 국,수,영,탐(1) 중 2개 합 8 / 보건과학대: 국,수,영,탐(1) 중 1개 4 / 안경광학과·의료경영학과: 없음",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("인하대(인천)", "학생부교과", "지역균형"): {
        "csat_minimum": "인문: 국,수,영,탐(1) 중 2개 합 6 / 자연: 국,수,영,탐(1) 중 2개 합 5 / 의예: 국,수,영,과(절사) 중 3개 합 4",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("전북대(전주)", "학생부종합", "큰사람"): {
        "csat_minimum": "의예: 국,수(미/기),영,과 중 4개 합 6 / 치의예: 국,수(미/기),영,과(1) 중 3개 합 6(수 포함) / 약학: 국,수(미/기),영,과(1) 중 3개 합 7(수 포함) / 간호: 국,수,영,탐(1) 중 2개 합 6",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("전북대(전주)", "학생부종합", "지역인재1"): {
        "csat_minimum": "의예: 국,수(미/기),영,과 중 4개 합 6 / 약학: 국,수(미/기),영,과(1) 중 3개 합 7(수 포함) / 간호: 국,수,영,탐(1) 중 2개 합 6",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("전북대(특성화)", "학생부종합", "큰사람"): {
        "csat_minimum": "수의예: 국,수(미/기),영,과(1) 중 3개 합 7(수 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("조선대(광주)", "학생부종합", "면접"): {
        "csat_minimum": "의예·치의예: 국,수(미/기),영,과(1) 중 3개 합 5(수 포함) / 약학: 국,수(미/기),영,과(1) 중 3개 합 6(수 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("조선대(광주)", "학생부종합", "서류"): {
        "csat_minimum": "의예·치의예: 국,수(미/기),영,과(1) 중 3개 합 5(수 포함) / 약학: 국,수(미/기),영,과(1) 중 3개 합 6(수 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("차 의과학대(포천)", "학생부교과", "지역균형선발"): {
        "csat_minimum": "약학: 국,수,영,탐(절사) 중 3개 합 6(수 포함)",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("충남대(대전)", "학생부종합", "학생부종합Ⅰ(면접(200))"): {
        "csat_minimum": "간호: 국,수,영,탐/직(1) 중 3개 합 12",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("충남대(대전)", "학생부종합", "학생부종합Ⅰ(면접(300))"): {
        "csat_minimum": "의예: 국,수(미/기),영,과 중 3개 합 5(수 포함) / 수의예: 국,수(미/기),영,과 중 3개 합 7(수 포함) / 수학교육: 국,수(미/기),영,탐(1)/직 중 3개 합 10(수 포함) / 국어교육·영어교육·교육학과: 국,수,영,탐/직(1) 중 3개 합 10 / 건설공학교육·기계공학교육·화학공학교육·기술교육: 국,수,영,탐/직(1) 중 3개 합 12",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("충북대(청주)", "학생부종합", "학생부종합Ⅱ"): {
        "csat_minimum": "인문사회계열: 국,수,영,탐/직(1) 중 2개 합 8 / 공학계열·바이오헬스: 국,수,영,과(1) 중 2개 합 8 / 수학·정보통계: 국,수(미/기),영,과(1) 중 2개 합 8(수 포함) / 의예: 국,수(미/기),영,과(1) 중 3개 합 5(수 포함) / 약학·제약학: 국,수(미/기),영,과(1) 중 3개 합 7(수 포함) / 수의예: 국,수,영,과(1) 중 3개 합 8 / 간호: 국,수,영,탐(1) 중 2개 합 6 / 자연과학·자율전공: 국,수,영,탐(1) 중 2개 합 8",
        "notes": "공통: 국,수,영,탐(1) 응시 필수",
    },
    ("포항공과대(포항)", "학생부종합", "일반Ⅱ"): {
        "csat_minimum": "단일계열: 국,수(미/기),영,과 중 2개 합 4(수 포함)",
        "notes": "학생부종합전형 수능최저 상세표 기준",
    },
    ("한국교원대(청주)", "학생부종합", "학생부종합우수자"): {
        "csat_minimum": "일반 인문사회·수학교육 등: 국,수,영,탐 중 4개 합 14 / 가정·환경·기술·컴퓨터·음악·체육교육 등: 국,수,영,탐/직 중 4개 합 14",
        "notes": "일부 자연계 교육과는 수(미/기) 또는 과탐 1등급 상향 조건 적용",
    },
    ("한국외국어대(글로벌)", "학생부교과", "학교장추천"): {
        "csat_minimum": "국,수,영,탐(1) 중 2개 합 6",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
    ("한양대(ERICA)", "학생부교과", "지역균형선발"): {
        "csat_minimum": "국,수,영,탐(1) 중 2개 합 7 / 약학: 국,수,영,탐(1) 중 3개 합 5",
        "notes": "학생부교과전형 수능최저 상세표 기준",
    },
}

TARGET_SECTION_FILES = [
    "05-student-record-subject.md",
    "06-student-record-comprehensive.md",
    "07-essay.md",
    "08-suneung.md",
    "09-opportunity-integrated.md",
    "10-rural.md",
    "11-low-income.md",
    "12-vocational.md",
    "13-disability.md",
    "14-regional.md",
    "15-medical-overview.md",
    "16-medical-features.md",
    "17-medical-analysis.md",
    "18-education.md",
    "19-science-specialized.md",
    "20-major-free-choice.md",
    "21-contract-cutting-edge.md",
    "22-arts-sports.md",
    "25-university-directory.md",
]

REGIONS = {"서울", "인천", "경기", "강원", "대전", "세종", "충남", "충북", "대구", "경북", "부산", "울산", "경남", "광주", "전남", "전북", "제주"}


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    _, rest = text.split("---\n", 1)
    meta_text, body = rest.split("\n---\n", 1)
    return json.loads(meta_text), body


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9가-힣]+", "-", value.lower()).strip("-")
    return slug or "university"


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", "", name)


def base_name(name: str) -> str:
    return re.sub(r"\([^)]+\)", "", name).strip()


def classify_campus(name: str) -> str:
    if "(" in name and ")" in name:
        return name[name.find("(") + 1 : name.find(")")]
    return "본교"


def parse_directory_entries(text: str) -> dict[str, dict]:
    entries: dict[str, dict] = {}
    current_region = ""
    page = None
    region_pattern = "|".join(sorted(REGIONS, key=len, reverse=True))
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("## 원본 페이지"):
            match = re.search(r"원본 페이지 (\d+)", line)
            page = int(match.group(1)) if match else None
            continue
        if line in REGIONS:
            current_region = line
            continue
        if "http" not in line:
            continue
        match = re.match(r"(.+?)\s+(https?://\S+)\s+([0-9()\-~]+(?:\s*,\s*[0-9()\-~]+)*)\s+(.+)$", line)
        if not match:
            match = re.match(rf"(.+?)\s+(https?://\S+)\s+(.+?)\s*((?:{region_pattern}).+)$", line)
        if not match:
            continue
        name, website, phone, address = match.groups()
        entries[name] = {
            "id": slugify(name),
            "name": name,
            "base_name": base_name(name),
            "campus": classify_campus(name),
            "normalized_name": normalize_name(name),
            "region": current_region,
            "website": website,
            "admission_url": ADMISSION_URL_OVERRIDES.get(name, website),
            "phone": phone,
            "address": address,
            "directory_page": page,
        }
    entries.update(MANUAL_DIRECTORY_ENTRIES)
    return entries


def parse_page_blocks(body: str) -> list[tuple[int | None, list[str]]]:
    blocks: list[tuple[int | None, list[str]]] = []
    current_page = None
    current_lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## 원본 페이지"):
            if current_lines:
                blocks.append((current_page, current_lines))
            match = re.search(r"원본 페이지 (\d+)", line)
            current_page = int(match.group(1)) if match else None
            current_lines = []
            continue
        current_lines.append(line)
    if current_lines:
        blocks.append((current_page, current_lines))
    return blocks


def compact_lines(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines if line.strip()]


def build_alias_pairs(directory_entries: dict[str, dict]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for name, meta in directory_entries.items():
        pairs.append((name, name))
        if meta["campus"] == "본교":
            pairs.append((meta["base_name"], name))
    unique_pairs = sorted(set(pairs), key=lambda item: len(item[0]), reverse=True)
    return unique_pairs


def build_base_name_counts(directory_entries: dict[str, dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for meta in directory_entries.values():
        counts[meta["base_name"]] += 1
    return dict(counts)


def build_evidence_record(
    *,
    university_name: str,
    alias: str,
    section_id: str,
    section_title: str,
    page: int | None,
    context: list[str],
) -> dict:
    snippet = " ".join(context)
    return {
        "university_name": university_name,
        "matched_alias": alias,
        "section_id": section_id,
        "section_title": section_title,
        "page": page,
        "snippet": snippet[:700],
        "keywords": sorted(
            {
                keyword
                for keyword in ["모집인원", "전형방법", "수능최저", "교과", "종합", "논술", "정시", "면접", "서류", "지역인재", "기회균형"]
                if keyword in snippet
            }
        ),
    }


def apply_csat_minimum_overrides(university_name: str, admissions: list[dict]) -> list[dict]:
    updated = copy.deepcopy(admissions)
    for admission in updated:
        key = (
            university_name,
            admission.get("admission_type", ""),
            admission.get("track_name", ""),
        )
        override = CSAT_MINIMUM_OVERRIDES.get(key)
        if not override:
            continue
        admission["csat_minimum"] = override["csat_minimum"]
        if override.get("notes"):
            admission["notes"] = override["notes"]
    return updated


def build_dataset() -> tuple[dict, list[dict]]:
    section_records = []
    directory_entries: dict[str, dict] = {}
    for filename in TARGET_SECTION_FILES:
        path = SECTIONS_DIR / filename
        meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
        section_records.append((filename, meta, body))
        if filename == "25-university-directory.md":
            directory_entries = parse_directory_entries(body)

    alias_pairs = build_alias_pairs(directory_entries)
    base_name_counts = build_base_name_counts(directory_entries)
    evidence_by_university: dict[str, list[dict]] = defaultdict(list)
    seen_signatures: dict[str, set[tuple]] = defaultdict(set)

    for filename, meta, body in section_records:
        if filename == "25-university-directory.md":
            continue
        section_id = meta.get("id", filename)
        section_title = meta.get("title", filename)
        for page, lines in parse_page_blocks(body):
            compact = compact_lines(lines)
            for idx, line in enumerate(compact):
                for alias, university_name in alias_pairs:
                    if alias and alias in line:
                        start = max(0, idx - 1)
                        end = min(len(compact), idx + 3)
                        context = compact[start:end]
                        record = build_evidence_record(
                            university_name=university_name,
                            alias=alias,
                            section_id=section_id,
                            section_title=section_title,
                            page=page,
                            context=context,
                        )
                        signature = (record["section_id"], record["page"], record["snippet"])
                        if signature in seen_signatures[university_name]:
                            continue
                        seen_signatures[university_name].add(signature)
                        evidence_by_university[university_name].append(record)

    universities = []
    flat_evidence = []
    for name in sorted(directory_entries):
        meta = directory_entries[name]
        evidence = evidence_by_university.get(name, [])
        curated_admissions = CURATED_ADMISSIONS.get(name, [])
        if not curated_admissions and base_name_counts.get(meta["base_name"], 0) == 1:
            curated_admissions = CURATED_ADMISSIONS.get(meta["base_name"], [])
        curated_admissions = apply_csat_minimum_overrides(name, curated_admissions)
        summary = []
        for item in evidence:
            parts = [item["section_title"]]
            if item["page"] is not None:
                parts.append(f"PDF {item['page']}")
            if item["keywords"]:
                parts.append(", ".join(item["keywords"]))
            summary.append(" · ".join(parts))
            if len(summary) >= 4:
                break

        university = {
            "id": meta["id"],
            "name": meta["name"],
            "base_name": meta["base_name"],
            "campus": meta["campus"],
            "normalized_name": meta["normalized_name"],
            "search_terms": sorted({meta["name"], meta["base_name"], meta["normalized_name"], normalize_name(meta["base_name"])}),
            "region": meta["region"],
            "website": meta["website"],
            "admission_url": meta.get("admission_url", meta["website"]),
            "phone": meta["phone"],
            "address": meta["address"],
            "directory_page": meta["directory_page"],
            "structured_admissions": curated_admissions,
            "evidence_count": len(evidence),
            "evidence_summary": summary,
            "evidence_preview": [
                {
                    "section_title": item["section_title"],
                    "page": item["page"],
                    "keywords": item["keywords"],
                    "snippet": item["snippet"],
                }
                for item in evidence[:8]
            ],
            "data_status": {
                "directory_profile": True,
                "structured_admissions_ready": bool(curated_admissions),
                "evidence_collected": bool(evidence),
            },
        }
        universities.append(university)
        flat_evidence.extend(evidence)

    dataset = {
        "schema_version": "2.0.0",
        "generated_from": str(SOURCE_DIR),
        "counts": {
            "universities": len(universities),
            "evidence_records": len(flat_evidence),
        },
        "universities": universities,
    }
    return dataset, flat_evidence


def main() -> None:
    DERIVED_DIR.mkdir(parents=True, exist_ok=True)
    dataset, evidence_records = build_dataset()
    OUT_JSON.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_CATALOG.write_text(json.dumps(dataset["universities"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with OUT_EVIDENCE.open("w", encoding="utf-8") as fp:
        for record in evidence_records:
            fp.write(json.dumps(record, ensure_ascii=False) + "\n")
    OUT_JS.write_text("window.UNIVERSITY_DATA = " + json.dumps(dataset, ensure_ascii=False) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
