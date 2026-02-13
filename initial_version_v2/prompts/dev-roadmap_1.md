## Phase 9: 검색 고도화 및 데이터 인사이트 (기능 개선)

---

### 1. 추가 및 개선되는 기능 요약
1. 세부 검색 필터 (Advanced Search): 기간(최근 하루~1년), 특정 도메인 선택, 검색 언어 설정을 통해 검색 노이즈를 제거합니다.

2. 다중 키워드 논리 검색 (Boolean Search): + 또는 공백을 활용한 필수 포함어 필터링 기능을 추가합니다.

3. 실시간 검색 트렌드 (Search Insights): 전체 사용자들이 검색한 키워드 빈도를 분석하여 메인 화면에 '인기 검색어 랭킹'을 시각화합니다.

4. 검색 결과 내 필터링 (In-depth Filtering): (AI 추천) 검색된 결과 내에서 특정 단어가 포함된 기사만 다시 추려보는 기능을 추가했습니다.

#### 1단계: 도메인 및 리포지토리 확장
domain/search_params.py (신규)
 - 검색 조건을 관리하는 SearchParams 데이터클래스:
  - date_range: str ("d", "w", "m", "y" - 하루, 주, 달, 년)
  - language: str ("ko", "en")
  - include_domains: List[str]
  - exclude_keywords: List[str]

repositories/search_repository.py (수정)
 - get_popular_keywords(limit: int = 5) -> List[tuple]
  - CSV 데이터를 분석하여 가장 많이 검색된 키워드 상위 N개를 반환합니다.

#### 2단계: 서비스 레이어 고도화 (services/)
services/search_service.py (수정)
 - search_news(keyword: str, params: SearchParams, num_results: int = 5)
 - 다중 키워드 처리: keyword에 포함된 + 기호를 분석하여 Tavily 쿼리를 최적화합니다.
 - Tavily 파라미터 적용:
  - search_depth: "advanced"
  - time_range: params.date_range 적용
  - include_domains: 설정에서 선택된 도메인만 전달

services/insight_service.py (신규)
 - analyze_trending_topics(df: pd.DataFrame)
  - 최근 검색 기록에서 키워드 빈도수를 계산하여 트렌드 데이터를 생성합니다.

#### 3단계: UI 컴포넌트 개선 (components/)
components/search_form.py (수정)
 - 상세 설정 Expander 추가:
  - 기간 선택 (Radio/Selectbox): 오늘, 이번 주, 이번 달, 올해
  - 언어 선택 (Toggle): 한국어, 영어
  - 필수 포함 단어 입력 필드 추가 (+ 연산 기능 안내)

components/dashboard.py (신규)
 - render_trending_keywords(trending_data)
  - 메인 화면 상단에 "🔥 지금 많이 검색하는 키워드"를 배치합니다.
  - 배지(Badge) 형태의 UI로 가독성을 높입니다.

#### 4단계: 메인 앱 통합 (app.py)
1. 앱 시작 시 인사이트 로드: repository.load()를 통해 기존 데이터를 읽어 실시간 순위를 먼저 계산합니다.

2. 레이아웃 변경: - 상단: 실시간 인기 키워드 섹션
 - 중앙: 상세 필터가 포함된 검색 폼
 - 하단: 결과 및 요약 섹션

 ---

### 검증 포인트
- [ ] 고양이 + 젤리 입력 시 두 단어가 모두 포함된 결과가 우선순위로 나오는지 확인
- [ ] 검색 기간을 '오늘'로 설정했을 때 과거 기사가 제외되는지 확인
- [ ] 메인 화면 상단에 검색 빈도가 높은 키워드 순위가 표시되는지 확인
- [ ] 영어 뉴스 검색 시 Gemini가 한글로 요약을 수행하는지 확인

---

### ⚠️ 필수 요구사항: 한글 사용
모든 필터 레이블은 한글로 작성합니다. (예: "기간 설정", "검색 언어", "필수 포함어")

인기 순위 제목: "🔥 실시간 인기 검색 키워드"

기간 옵션: "최근 24시간", "최근 1주", "최근 1개월", "최근 1년"

---

### 🚫 금지사항: Git/GitHub 작업 금지
Git 및 GitHub 관련 작업은 일절 하지 마세요.