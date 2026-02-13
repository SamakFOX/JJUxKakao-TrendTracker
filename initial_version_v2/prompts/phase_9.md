# Phase 9: 고급 검색 / 트렌드 UI 개선 (7단계 중 8단계)

---

Phase 9에서는 검색 UX를 고도화하고, 사용자의 재검색 및 탐색을 유도하는 기능을 추가합니다.  
본 Phase는 **기존 CSV 기반 저장 구조를 유지**하며, DB 도입 없이 구현합니다.

---

## 0. 구현 목표 요약

- 검색 범위를 사용자가 직접 제어할 수 있도록 개선
- OR 기본 다중 검색어 + AND / NOT 조건 검색 UI 제공
- 앱 내부 검색 로그 기반 실시간 인기 검색어 제공
- 검색 결과 기반 연관 키워드 제안 기능 추가

---

## 1. 구현 범위 (이번 Phase에서 구현할 기능)

### 1) 검색 범위 지정
- 기간(Date) 필터
  - 최근 24시간
  - 최근 7일
  - 최근 30일
  - 직접 선택(시작일 / 종료일)
- 도메인(Domain) 필터
  - 카테고리 프리셋 기반
  - 다중 선택 가능
  - 체크박스가 아닌 “칩(버튼)” UI
  - 선택 시 색상 변경, 재클릭 시 해제

---

### 2) 다중 검색어 + 조건 검색 UI (OR 기본)

- 기본 검색 로직: **OR 검색**
  - 메인 검색창에 여러 단어 입력 시 OR 처리
  - 예: `고양이, 강아지`
- 검색창 우측에 “조건” 버튼 배치
- 버튼 클릭 시 조건 패널 표시
- 조건 패널 구성:
  - AND 조건 입력 영역 (50%)
  - NOT 조건 입력 영역 (50%)

#### UI 힌트 메시지 (한글 고정)
- AND: “여기에 입력한 단어는 기사에 반드시 포함되어야 합니다. (쉼표로 여러 개 입력 가능)”
- NOT: “여기에 입력한 단어가 포함된 기사는 제외됩니다. (쉼표로 여러 개 입력 가능)”

---

### 3) 실시간 인기 검색어 (앱 내부 기준)

- CSV(search_history.csv)에 저장된 검색 기록을 기반으로 집계
- 기준: 최근 24시간 검색 횟수
- Top 10 키워드 표시
- 메인 화면 상단 또는 사이드바 상단에 노출
- 키워드 클릭 시:
  - 검색어로 자동 입력
  - 즉시 재검색 실행

---

### 4) 연관 키워드 확장 (검색 결과 기반)

- 검색 결과 기사들의 제목 + 스니펫을 기반으로 연관 키워드 생성
- 외부 빅데이터 / 트렌드 API 사용하지 않음
- AI 요약 호출 시 연관 키워드를 함께 생성
- 결과 화면에서 가로형 버튼 리스트로 표시
- 버튼 클릭 시 해당 키워드로 재검색

---

## 2. Session State 설계

```python
# 검색 입력
search_main_raw: str
search_and_raw: str
search_not_raw: str

# 조건 패널 토글
show_advanced_filters: bool

# 기간 필터
date_filter_mode: str          # "24h" | "7d" | "30d" | "custom"
date_custom_start: Optional[date]
date_custom_end: Optional[date]

# 도메인 카테고리
selected_domain_categories: List[str]

# 결과/모드
last_result: Optional[SearchResult]
current_mode: str              # "new_search" | "history"
selected_key: Optional[str]

# 트렌딩/재검색
pending_keyword: Optional[str]
```

---

## 3. 신규 / 변경 파일 구조
```
utils/
 └─ query_builder.py          # 검색 쿼리 조합 로직

components/
 ├─ search_form.py            # 조건 패널 포함 검색 UI
 ├─ chips.py                  # 도메인 카테고리 칩 UI
 ├─ trending_section.py       # 실시간 인기 검색어 UI
 └─ result_section.py         # 연관 키워드 영역 추가

services/
 ├─ search_service.py         # 조건 기반 검색 확장
 └─ ai_service.py             # 요약 + 연관 키워드 동시 생성

repositories/
 └─ search_repository.py      # 인기 검색어 집계 메서드 추가
```

---

## 4. 검색 조건 데이터 구조
```python
from dataclasses import dataclass
from datetime import date
from typing import List, Optional

@dataclass
class SearchFilters:
    main_terms: List[str]        # OR 기본
    and_terms: List[str]
    not_terms: List[str]
    date_filter_mode: str        # "24h" | "7d" | "30d" | "custom"
    custom_start: Optional[date]
    custom_end: Optional[date]
    include_domains: List[str]
```

---

## 5. Query Builder (utils/query_builder.py)
```python
def parse_terms(raw: str) -> List[str]:
    """
    쉼표(,) 기준 분리 + trim + 빈 값 제거
    """

def build_query(filters: SearchFilters) -> str:
    """
    OR 기본 쿼리 생성
    예:
    (고양이 OR 강아지) AND 젤리 NOT 사료
    """

def resolve_days(
    date_filter_mode: str,
    custom_start: Optional[date],
    custom_end: Optional[date]
) -> Optional[int]:
    """
    Tavily 검색용 최근 N일 값 반환
    """
```

---

## 6. 도메인 카테고리 설정 (config/settings.py)
```python
DOMAIN_CATEGORIES = {
  "국내 종합": [...],
  "방송/통신": [...],
  "경제": [...],
  "IT/테크": [...]
}
```

---

## 7. 검색 서비스 변경 (services/search_service.py)
```python
def search_news(filters: SearchFilters, num_results: int = 5) -> List[NewsArticle]:
    """
    - build_query(filters) 결과를 query로 사용
    - include_domains, 기간 필터 적용
    - 최신순 정렬 후 num_results 개 반환
    """
```

---

## 8. AI 요약 + 연관 키워드 생성 (services/ai_service.py)
```python
from dataclasses import dataclass
from typing import List

@dataclass
class AiOutput:
    summary: str
    related_keywords: List[str]

def summarize_news_with_keywords(articles: List[NewsArticle]) -> AiOutput:
    """
    - 뉴스 요약 (불릿 최대 5)
    - 연관 키워드 5~10개 생성
    """
```

---

## 9. 인기 검색어 집계 (repositories/search_repository.py)
```python
def get_trending_keywords(self, hours: int = 24, limit: int = 10) -> List[str]:
    """
    최근 hours 시간 기준 keyword count 집계
    """
```

---

## 10. UI 요구사항 (한글 고정)
검색 영역
 - 검색어
 - 검색
 - 조건
 - 포함(AND)
 - 제외(NOT)

인기 검색어
 - 제목: “🔥 실시간 인기 검색어”
 - 빈 상태: “아직 검색 기록이 없습니다. 키워드를 입력해 첫 검색을 시작해보세요!”

연관 키워드
 - 제목: “🔁 연관 키워드”
 - 가로 버튼 리스트

 ---

 ## 11. CSV / DB 관련 정책
  - DB 도입하지 않음
  - 기존 CSV 기반 저장 방식 유지
  - 인기 검색어, 조건 검색 모두 CSV로 처리
  - 필요 시 컬럼 확장 가능하나 Phase 9에서는 필수 아님

---

### 구현 요구사항
- 모든 에러 메시지는 사용자 친화적으로 작성
- 기술적 에러 내용은 로그로만 기록
- README.md는 초보자도 따라할 수 있도록 상세히 작성

---

## 12. 검증 체크리스트
- [ ]  OR 기본 검색 정상 동작
- [ ]  AND / NOT 조건 반영 확인
- [ ]  기간 필터 적용 확인
- [ ]  도메인 카테고리 칩 토글 정상
- [ ]  실시간 인기 검색어 표시 및 클릭 동작
- [ ]  연관 키워드 버튼 표시 및 재검색
- [ ]  CSV 비어있어도 앱 크래시 없음

---

### ⚠️ 필수 요구사항: 한글 사용

**최종 점검 - 모든 UI가 한글인지 확인해주세요:**
- 환경변수 누락 안내 메시지
- API 에러 메시지
- 진행 상태 표시 메시지
- 성공/실패 메시지
- 빈 상태 안내 메시지
- README.md 제외 모든 사용자 대면 텍스트

**앱 실행 시 영어로 된 UI 텍스트가 보이면 한글로 수정해주세요!**

---

### 🚫 금지사항: Git/GitHub 작업 금지

**Git 및 GitHub 관련 작업은 일절 하지 마세요.**