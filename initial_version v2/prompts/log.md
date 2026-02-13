# 생성 로그

## 프로젝트 초기화 및 환경 설정(Phase 1)을 완료했습니다. 진행된 작업 내용은 다음과 같습니다.
### 진행 로그
1. 프로젝트 초기화: uv init . 명령을 통해 initial_version 프로젝트를 초기화했습니다.
2. 가상환경 설정: Python 3.11 기반의 가상환경(.venv)을 생성했습니다.
3. 의존성 패키지 설치: 다음 패키지들을 추가했습니다.
 - streamlit, pandas, google-genai, requests, python-dotenv, tavily-python
4. 폴더 구조 생성: 요구사항에 따라 다음 폴더들을 생성하고 각각 __init__.py 파일을 배치했습니다.
 - config/, domain/, repositories/, services/, components/, utils/, data/
5. 설정 파일 작성:
 - .env.example : API 키 및 설정을 위한 템플릿 파일을 생성했습니다.
 - config/settings.py : dotenv를 사용하여 환경 변수를 로드하고, 필수 변수(TAVILY_API_KEY, GEMINI_API_KEY, CSV_PATH) 누락 시 친절한 에러 메시지를 출력하는 Settings 클래스를 작성했습니다.
6. 메인 앱 파일 생성: 기본적인 구조를 갖춘 app.py를 생성했습니다.

### 검증 결과
 - .venv 폴더 생성 및 경로 확인 (.venv\Scripts\python.exe)
 - pyproject.toml 및 uv.lock 생성 완료
 - uv pip list를 통한 패키지 설치 확인 완료
 - config.settings 모듈 import 테스트 성공

⚠️ 중요: 다음 단계로 넘어가기 전에 .env 파일을 반드시 설정해주세요!

1. .env.example 파일을 .env로 복사합니다:
```bash
cp .env.example .env
```
2. .env 파일을 열어 다음 API 키를 모두 입력해주세요:
 - TAVILY_API_KEY: Tavily 웹사이트에서 발급
 - SEARCH_DOMAINS: 검색하고 싶은 뉴스/테크 사이트 도메인 (쉼표로 구분)
 - GEMINI_API_KEY: Google AI Studio에서 발급
※ 모든 API 키가 설정되어야 앱이 정상 동작합니다!
---

## 도메인 모델 및 유틸리티 함수(Phase 2)를 완료했습니다.
### 진행 로그
1. **도메인 모델 구현 (domain/)**:
    - `news_article.py`: 뉴스 기사 정보를 담는 `NewsArticle` 데이터클래스를 구현했습니다.
    - `search_result.py`: 검색 결과 및 AI 요약을 관리하는 `SearchResult` 데이터클래스를 구현했습니다. CSV 저장을 위한 `to_dataframe()` 메서드(Long format)를 포함합니다.
2. **유틸리티 함수 구현 (utils/)**:
    - `key_generator.py`: "키워드-날짜시간" 형식의 고유 키 생성 함수를 작성했습니다.
    - `input_handler.py`: 사용자 입력 키워드의 공백 제거 및 길이 제한(100자) 전처리 함수를 구현했습니다.
    - `error_handler.py`: Streamlit을 지원하는 에러 메시지 처리 시스템을 구축했습니다. (한글 메시지 적용)

### 검증 결과
- `NewsArticle` 및 `SearchResult` 모델 import 테스트 성공
- `generate_search_key`: "테스트-202602130200" 형식 생성 확인
- `preprocess_keyword`: 공백 제거 및 빈 문자열 처리(`None` 반환) 확인
- `SearchResult.to_dataframe()`: pandas DataFrame 변환 및 데이터 구조 확인 완료

---

## 서비스 레이어 - API 연동(Phase 3)을 완료했습니다.
### 진행 로그
1. **커스텀 예외 클래스 구현 (`utils/exceptions.py`)**:
    - 애플리케이션 전역에서 사용할 `AppError` 클래스를 정의했습니다.
2. **도메인 모델 업데이트 (`domain/news_article.py`, `domain/search_result.py`)**:
    - `NewsArticle`에 `pub_date`(발행일) 필드를 추가했습니다.
    - `SearchResult.to_dataframe()` 메서드가 `article_pub_date`를 포함하도록 업데이트했습니다.
3. **설정 관리 업데이트 (`config/settings.py`)**:
    - `Settings` 인스턴스를 싱글톤으로 사용할 수 있도록 내보내기를 활성화했습니다.
4. **뉴스 검색 서비스 구현 (`services/search_service.py`)**:
    - Tavily API를 사용하여 뉴스 검색 및 최신순 정렬 기능을 구현했습니다.
    - `search_depth="advanced"`, `topic="news"` 등의 옵션을 적용했습니다.
5. **AI 요약 서비스 구현 (`services/ai_service.py`)**:
    - Gemini API(google-genai)를 사용하여 뉴스 목록을 한국어로 요약하는 기능을 구현했습니다.
    - 불릿 포인트 형식의 요약 프롬프트를 적용했습니다.

### 검증 결과
- `AppError` import 및 동작 확인 완료
- `search_news` 및 `summarize_news` 모듈 import 성공
- API 호출 시 발생할 수 있는 주요 예외(API 키 오류, Rate Limit 등)에 대한 `AppError` 처리 확인
- `NewsArticle` 필드 확장에 따른 데이터 구조 정합성 확인

---

## 리포지토리 레이어 - 데이터 관리(Phase 4)를 완료했습니다.
### 진행 로그
1. **도메인 모델 업데이트 (`domain/search_result.py`)**:
    - `to_dataframe()` 메서드를 Phase 4 요구사항(8개 컬럼, `article_index` 추가)에 맞춰 수정했습니다.
2. **리포지토리 구현 (`repositories/search_repository.py`)**:
    - CSV 파일을 기반으로 검색 기록을 로드(`load`), 저장(`save`), 조회(`find_by_key`)하는 `SearchRepository` 클래스를 구현했습니다.
    - `data/` 폴더 자동 생성 및 인코딩(`utf-8-sig`) 처리를 포함합니다.
3. **UI 컴포넌트 생성 (`components/sidebar.py`)**:
    - "💾 데이터 저장 안내"를 포함한 사이드바 정보 렌더링 함수 `render_info()`를 구현했습니다.

### 검증 결과
- `SearchRepository` import 및 초기화 테스트 성공
- CSV 로드 시 8개 필수 컬럼(`search_key`, `search_time`, `keyword`, `article_index`, `title`, `url`, `snippet`, `ai_summary`) 확인 완료
- `data/` 폴더 자동 생성 확인
- 리포지토리 기본 동작(빈 파일 로드 등) 정상 확인

---

## UI 컴포넌트(Phase 5)를 완료했습니다.
### 진행 로그
1. **검색 폼 구현 (`components/search_form.py`)**:
    - 키워드 입력 필드와 검색 버튼을 포함한 `render_search_form()`을 구현했습니다.
    - 입력값 전처리 및 유효성 검사 로직을 포함합니다.
2. **사이드바 기능 확장 (`components/sidebar.py`)**:
    - 앱 제목, 검색 설정(슬라이더), 사용법 안내, 실시간 검색 기록 목록, CSV 다운로드 버튼 기능을 모두 구현했습니다.
    - 검색 기록은 "키워드 (날짜 시간)" 형식으로 가독성 있게 표시됩니다.
3. **결과 섹션 구현 (`components/result_section.py`)**:
    - AI 요약 결과를 보여주는 `render_summary()`와 뉴스 리스트를 expander 형태로 보여주는 `render_news_list()`를 구현했습니다.
4. **로딩 상태 관리 (`components/loading.py`)**:
    - `st.spinner`를 활용한 컨텍스트 매니저 방식의 `show_loading()`을 구현하여 사용자 경험을 개선했습니다.

### 검증 결과
- 모든 개별 UI 컴포넌트(`search_form`, `sidebar`, `result_section`, `loading`)의 import 테스트 성공
- 사이드바 설정값(1~10 범위) 및 검색 기록 선택 박스 동작 구조 확인
- 모든 UI 텍스트 및 안내 메시지 한글 적용 완료

---

## 메인 앱 통합(Phase 6)을 완료했습니다.
### 진행 로그
1. **메인 애플리케이션 통합 (`app.py`)**:
    - 모든 서비스, 리포지토리, UI 컴포넌트를 `app.py`로 결합하여 전체 워크플로우를 완성했습니다.
    - `st.set_page_config`를 통한 페이지 레이아웃 및 아이콘을 설정했습니다.
2. **상태 관리 및 모드 전환 구현**:
    - `st.session_state`를 활용하여 "새 검색(new_search)"과 "기록 조회(history)" 모드 간의 논리적 전환을 구현했습니다.
    - `st.rerun()`을 적시에 활용하여 사용자 인터랙션 후 즉각적인 UI 갱신이 이루어지도록 했습니다.
3. **통합 에러 핸들링**:
    - API 호출(검색, 요약) 및 파일 입출력 시 발생할 수 있는 오류를 `try-except`와 `handle_error()`를 통해 안전하게 처리했습니다.
4. **사이드바 기능 연동**:
    - 검색 건수 설정, 히스토리 목록 조회, 전체 데이터 CSV 다운로드 기능을 실제 비즈니스 로직과 연결했습니다.

### 검증 결과
- `app.py` 구문 오류 검사 및 컴파일 성공
- 세션 상태에 따른 모드 전환(검색 시 new_search, 히스토리 선택 시 history) 로직 확인
- 로딩 스피너(`show_loading`)가 각 단계별로 적절히 호출됨을 확인
- CSV 복원 및 `SearchResult` 객체 재구성 기능 통합 테스트 완료

---

## 에러 핸들링 강화 및 마무리(Phase 7)를 완료했습니다.
### 진행 로그
1. **에러 핸들링 강화**:
    - `config/settings.py`: 필수 환경변수 누락 시의 안내 메시지를 강화하고 API 키 발급 링크를 추가했습니다.
    - `services/search_service.py`: Tavily API 결과에 대한 상세 에러 처리(401, 429, 5xx)와 네트워크 장애 시 재시도 로직(1회)을 추가했습니다.
    - `services/ai_service.py`: Gemini API 할당량 초과 및 요청 오류에 대한 상세 예외 처리를 구현했습니다.
    - `utils/error_handler.py`: 강화된 에러 타입에 맞춰 한글 안내 메시지를 보강했습니다.
2. **UX 및 기능 개선**:
    - `app.py`: 검색 및 저장 단계별로 상세한 로딩 메시지("🔍 검색 중...", "💾 저장 중...")를 적용하고, 성공 안내 메시지를 추가했습니다.
    - 메인 화면에 초기 환영 메시지와 빈 히스토리 상태 안내 가이드를 구현했습니다.
3. **코드 정리 및 문서화**:
    - 프로젝트 내 모든 주요 클래스와 함수에 `docstring`을 추가하여 가독성을 높였습니다.
    - `README.md`: 프로젝트 소개, 폴더 구조, 설치 및 실행 방법, API 키 발급 안내를 포함한 전체 가이드를 작성했습니다.

### 검증 결과
- **설정 검증**: `.env` 파일 부재 시 명확하고 친절한 해결 방법이 출력됨을 확인했습니다.
- **E2E 테스트**: 검색 → 요약 → 자동 저장 → 히스토리 모드 전환 → CSV 다운로드로 이어지는 전체 사용자 흐름이 정상 동작함을 확인했습니다.
- **예외 처리**: 잘못된 API 키 사용 시 `AppError`를 통해 화면 상단에 한글 에러가 표시되며 앱이 크래시되지 않음을 확인했습니다.
- **한글화**: README를 제외한 모든 사용자 대면 텍스트가 한국어로 통일되었음을 최종 점검했습니다.

---

## 프로젝트 학습 가이드 생성(Phase 8)을 완료했습니다.
### 진행 로그
1. **학습 가이드 작성 (`MATERIAL.md`)**:
    - Phase 1부터 Phase 7까지의 전체 개발 과정을 집대성한 학습 문서를 생성했습니다.
    - 각 단계별 프롬프트의 역할, 핵심 배움 포인트, 주요 코드 스니펫(라인 번호 포함), 그리고 데이터 흐름도를 상세히 기술했습니다.
    - 주니어 개발자가 프로젝트 구조를 한눈에 파악하고 유지보수할 수 있도록 시니어 개발자의 관점에서 설명을 보강했습니다.
2. **최종 마감**:
    - 모든 소스 코드와 문서의 정렬 상태 및 일관성을 최종 확인했습니다.
    - 폴더 구조와 실제 구현 내용이 일치하는지 재검토했습니다.

### 검증 결과
- `MATERIAL.md` 내의 파일 경로 및 라인 번호가 실제 소스 코드와 일치함을 확인했습니다.
- 전체 데이터 흐름 시나리오(신규 검색, 기록 조회)가 실제 구현된 로직과 부합함을 확인했습니다.
- 프로젝트의 모든 산출물이 요구사항에 맞춰 준비되었습니다.

---

## 고급 검색 / 트렌드 UI 개선(Phase 9)을 완료했습니다.
### 진행 로그
1. **검색 기능 고도화**:
    - `domain/search_filters.py`: 검색어(OR/AND/NOT), 기간, 도메인 필터를 포함하는 `SearchFilters` 데이터 모델을 정의했습니다.
    - `utils/query_builder.py`: 다중 검색어 조합 및 기간 필터 변환 로직을 구현했습니다.
    - `services/search_service.py`: `SearchFilters`를 기반으로 Tavily API에 고급 쿼리 및 기간/도메인 필터를 적용하도록 확장했습니다.
2. **트렌드 및 연관 기능 구현**:
    - `repositories/search_repository.py`: 최근 24시간 검색 기록을 분석하여 인기 검색어 상위 10개를 집계하는 `get_trending_keywords` 기능을 추가했습니다.
    - `services/ai_service.py`: Gemini API를 활용하여 뉴스 요약과 동시에 5~10개의 연관 키워드를 자동 생성하는 `summarize_news_with_keywords`를 구현했습니다.
3. **UI/UX 개선**:
    - `components/chips.py`: 도메인 카테고리를 직관적으로 선택할 수 있는 “칩(버튼)” UI 컴포넌트를 생성했습니다.
    - `components/trending_section.py`: 실시간 인기 검색어를 메인 상단에 배치하고 클릭 시 바로 검색되는 기능을 구현했습니다.
    - `components/search_form.py`: AND/NOT 조건 및 기간 필터를 포함한 고급 검색 설정 가변 패널을 구축했습니다.
    - `components/result_section.py`: 결과 화면 하단에 AI가 제안하는 연관 키워드 탐색 영역을 추가했습니다.
4. **상태 관리 통합**:
    - `app.py`: 고급 검색을 위한 복합 세션 상태를 정의하고, 인기 검색어와 연관 키워드를 통한 재검색(`pending_keyword`) 워크플로우를 통합했습니다.

### 검증 결과
- **고급 검색**: OR(기본), AND(필수), NOT(제외) 로직이 포함된 복합 쿼리가 Tavily API에 정상 전달됨을 확인했습니다.
- **기간/도메인 필터**: 최근 24시간/7일/30일 및 특정 언론사 그룹별 필터링이 검색 결과에 반영됨을 확인했습니다.
- **인기 검색어**: CSV 기록 기반의 키워드 빈도 집계 및 클릭 시 자동 검색 연동 테스트를 완료했습니다.
- **연관 키워드**: AI 요약 결과와 함께 추출된 키워드들이 버튼 형태로 표시되며 재검색 기능을 지원함을 확인했습니다.

---

## 홈 화면 UX 강화 및 외부 트렌드 콘텐츠 추가(Phase 10)를 완료했습니다.
### 진행 로그
1. **홈 화면 UI 정렬 개선**:
    - `components/search_form.py`: 검색 입력창과 옵션 버튼을 한 줄로 정렬하고, 검색 실행 버튼을 중앙에 배치하여 시각적 균형을 맞췄습니다. `label_visibility="collapsed"`를 적용하여 불필요한 공백을 제거했습니다.
    - `components/trending_section.py`: 인기 검색어를 버튼(칩) 형태로 변경하고 6열 2줄(최대 12개)로 배치하여 공간 효율성을 높였습니다.
2. **외부 추천 콘텐츠 연동**:
    - `services/youtube_service.py`: YouTube Data API를 사용하여 한국 인기 급상승 영상 8개를 가져오는 서비스를 구현했습니다.
    - `services/trending_news_service.py`: 홈 화면 진입 시 실시간 트렌드 정보를 기반으로 추천 뉴스를 로드하는 기능을 추가했습니다.
3. **인터랙티브 컴포넌트 추가**:
    - `components/youtube_cards.py` & `components/news_cards.py`: 4열 그리드 형태의 카드 UI를 구현했습니다.
    - `components/popup_viewer.py`: `st.dialog`를 활용하여 유튜브 영상 임베드 재생 및 뉴스 상세 내용을 보여주는 통합 팝업 시스템을 구축했습니다.
4. **상태 관리 및 통합**:
    - `app.py`: 홈 추천 데이터의 프리페칭(Pre-fetching) 로직을 추가하여 페이지 전환 시에도 데이터를 유지하도록 했습니다. 검색 전 단계에서 추천 콘텐츠를 노출하여 앱 탐색성을 강화했습니다.

### 검증 결과
- **UI 정렬**: 검색 영역과 인기 검색어 영역이 요구사항에 맞춰 깔끔하게 정렬됨을 확인했습니다.
- **콘텐츠 로딩**: 유튜브 인기 영상과 트렌딩 뉴스가 홈 하단에 4열 그리드로 정상 노출됩니다.
- **팝업 동작**: 카드 클릭 시 팝업이 활성화되어 유튜브 영상 재생 및 뉴스 상세 정보(새 탭 링크 포함)가 한글로 정상 표시됨을 확인했습니다.
- **검색 연동**: 인기 검색어 클릭 시 즉시 검색이 실행되며 검색 결과 화면으로 전환되는 워크플로우를 검증했습니다.

---
**Phase 10: 홈 화면 UX 강화 및 트렌드 미디어 콘텐츠 확장이 성공적으로 완료되었습니다.**

