# TrendTracker 학습 가이드

이 문서는 TrendTracker 프로젝트를 7단계 프롬프트 순서에 따라 이해하기 위한 학습 가이드입니다. 각 Phase별로 **프롬프트 역할**, **핵심 개념**, **주요 코드**, **데이터 흐름**을 설명합니다.

---

# 목차

1. [Phase 1: 프로젝트 초기화 및 환경 설정](#phase-1-프로젝트-초기화-및-환경-설정)
2. [Phase 2: 도메인 모델 및 유틸리티 함수](#phase-2-도메인-모델-및-유틸리티-함수)
3. [Phase 3: 서비스 레이어 - API 연동](#phase-3-서비스-레이어---api-연동)
4. [Phase 4: 리포지토리 레이어 - 데이터 관리](#phase-4-리포지토리-레이어---데이터-관리)
5. [Phase 5: UI 컴포넌트](#phase-5-ui-컴포넌트)
6. [Phase 6: 메인 앱 통합](#phase-6-메인-앱-통합)
7. [Phase 7: 에러 핸들링 강화 및 마무리](#phase-7-에러-핸들링-강화-및-마무리)
8. [전체 데이터 흐름 다이어그램](#전체-데이터-흐름-다이어그램)

---

# Phase 1: 프로젝트 초기화 및 환경 설정

## 이 프롬프트의 역할
- 프로젝트의 기반이 되는 환경을 구축하고 설정을 관리하는 코드 생성
- 생성된 파일: `pyproject.toml`, `.env.example`, `config/settings.py`

## 학습 목표
- `uv` 패키지 매니저를 활용한 가상환경 및 의존성 관리 이해
- `python-dotenv`를 이용한 환경변수 로드 및 유효성 검사 패턴 학습

## 이해를 위한 핵심 개념

### 1.1 환경 변수 관리 (Settings)
애플리케이션은 실행 환경(로컬, 서버 등)에 따라 API 키나 파일 경로가 달라질 수 있습니다. 이를 코드에 직접 쓰지 않고 `.env` 파일에 분리하여 관리하는 것은 보안과 유지보수의 기본입니다.

### 1.2 패키지 매니저 (uv)
`uv`는 Rust로 작성된 매우 빠른 Python 패키지 매니저로, `pip`보다 속도가 빠르고 가상환경 관리가 간편합니다.

## 주요 코드 인용

### `config/settings.py` - 싱글톤 설정 관리
```python
# config/settings.py:1-48
import os
from dotenv import load_dotenv

class Settings:
    def __init__(self):
        load_dotenv()
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.CSV_PATH = os.getenv("CSV_PATH")
        self._validate()

    def _validate(self):
        missing = []
        if not self.TAVILY_API_KEY: missing.append("TAVILY_API_KEY")
        if missing:
            raise ValueError(f"필수 환경 변수가 누락되었습니다: {missing}")

settings = Settings()
```

**코드 설명:**
- `load_dotenv()`: `.env` 파일의 변수를 시스템 환경 변수로 로드합니다.
- `settings = Settings()`: 다른 모듈에서 동일한 설정 인스턴스를 공유하도록 싱글톤 패턴을 적용합니다.

## 데이터 흐름에서의 역할

```
┌─────────────────────────────────────┐
│         Phase 1 데이터 흐름          │
├─────────────────────────────────────┤
│                                     │
│  [.env] → [Settings 클래스] → [전역 변수] │
│                                     │
└─────────────────────────────────────┘
```

---

# Phase 2: 도메인 모델 및 유틸리티 함수

## 이 프롬프트의 역할
- 비즈니스 로직에 사용될 데이터 구조(도메인 모델)와 공통 유틸리티 생성
- 생성된 파일: `domain/news_article.py`, `domain/search_result.py`, `utils/key_generator.py`, `utils/input_handler.py`, `utils/error_handler.py`

## 학습 목표
- `dataclass`를 활용한 불변 데이터 구조 정의 학습
- 입출력값 전처리 및 고유 식별자(PK) 생성 로직 이해

## 이해를 위한 핵심 개념

### 2.1 도메인 모델 (Data Class)
비즈니스에서 다루는 핵심 정보(뉴스 기사, 검색 결과)를 객체지향적으로 표현합니다. `dataclass`는 보일러플레이트 코드를 줄여줍니다.

### 2.2 입력값 정제 (Sanitization)
사용자가 입력한 검색어의 공백을 제거하거나 길이를 제한하여 시스템의 안정성을 확보합니다.

## 주요 코드 인용

### `domain/search_result.py` - 데이터 ↔ 데이터프레임 변환
```python
# domain/search_result.py:25-41
    def to_dataframe(self) -> pd.DataFrame:
        data = []
        for i, article in enumerate(self.articles, 1):
            data.append({
                "search_key": self.search_key,
                "search_time": self.search_time.strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": self.keyword,
                "article_index": i,
                "title": article.title,
                "url": article.url,
                "snippet": article.snippet,
                "ai_summary": self.ai_summary
            })
        return pd.DataFrame(data)
```

**코드 설명:**
- `to_dataframe()`: 저장소(CSV)에 기록하기 전, 객체 리스트를 2차원 표 형식(Pandas DataFrame)으로 변환합니다.

## 데이터 흐름에서의 역할

```
┌─────────────────────────────────────┐
│         Phase 2 데이터 흐름          │
├─────────────────────────────────────┤
│                                     │
│  [Raw Data] → [Domain Objects]      │
│           (NewsArticle, SearchResult)│
│                                     │
└─────────────────────────────────────┘
```

---

# Phase 3: 서비스 레이어 - API 연동

## 이 프롬프트의 역할
- 외부 서비스(Tavily 검색 API, Gemini AI API)와 통신하는 비즈니스 로직 구현
- 생성된 파일: `services/search_service.py`, `services/ai_service.py`, `utils/exceptions.py`

## 학습 목표
- 외부 라이브러리(SDK)를 활용한 API 연동 및 결과 파싱 방법 습득
- 사용자 정의 예외(`AppError`)를 통한 예외 계층 구조 관리

## 이해를 위한 핵심 개념

### 3.1 API 통합 패턴
검색 로직(Tavily)과 요약 로직(Gemini)을 각각 서비스 클래스(또는 함수)로 분리하여 코드의 결합도를 낮춥니다.

### 3.2 최신순 뉴스 검색
검색 엔진으로부터 많은 결과를 가져온 뒤, 발행일(`pub_date`)을 기준으로 정렬하여 사용자에게 최신 트렌드를 제공합니다.

## 주요 코드 인용

### `services/ai_service.py` - AI 요약 프롬프트
```python
# services/ai_service.py:34-46
        prompt = f"""
다음 뉴스 기사들의 핵심 내용을 한국어로 요약해주세요:
- 불릿 포인트 형식으로 최대 5개 항목
- 각 항목은 1~2문장

[뉴스 목록]
{news_context}
        """
        response = client.models.generate_content(model=settings.GEMINI_MODEL, contents=prompt)
```

**코드 설명:**
- `prompt`: AI(Gemini)에게 수행할 작업과 컨텍스트(뉴스 목록)를 명확히 전달하는 프롬프트 엔지니어링 단계입니다.

## 데이터 흐름에서의 역할

```
┌─────────────────────────────────────────────────────────────┐
│                   Phase 3 데이터 흐름                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Keyword] → (Tavily 검색) → [NewsArticles] → (Gemini 요약) → [Summary] │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# Phase 4: 리포지토리 레이어 - 데이터 관리

## 이 프롬프트의 역할
- 검색 결과를 로컬 파일(CSV)에 영구 저장하고 불러오는 영속성 계층 구현
- 생성된 파일: `repositories/search_repository.py`

## 학습 목표
- Pandas를 활용한 CSV 파일 입출력 및 데이터 조회 로직 구현
- 파일이 없을 때의 예외 처리 및 폴더 자동 생성 기법 이해

## 이해를 위한 핵심 개념

### 4.1 리포지토리 패턴
데이터 소스(CSV 파일)에 접근하는 로직을 서비스 레이어와 분리하여, 저장 방식이 바뀌어도 비즈니스 로직은 수정되지 않게 합니다.

### 4.2 중복 제거 및 최신순 정렬
기사 1건당 1행으로 저장된 데이터를 불러올 때 `search_key` 기준으로 고유한 검색 세션을 추출하고 시간순으로 정렬합니다.

## 주요 코드 인용

### `repositories/search_repository.py` - CSV 저장 로직
```python
# repositories/search_repository.py:53-61
        try:
            new_df = search_result.to_dataframe()
            if os.path.exists(self.csv_path):
                existing_df = pd.read_csv(self.csv_path)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            combined_df.to_csv(self.csv_path, index=False, encoding='utf-8-sig')
```

**코드 설명:**
- `pd.concat`: 기존 데이터프레임 뒤에 새로운 검색 결과를 붙여(append) 업데이트합니다.
- `encoding='utf-8-sig'`: 한글 엑셀 깨짐 방지를 위해 BOM을 포함한 UTF-8을 사용합니다.

## 데이터 흐름에서의 역할

```
┌─────────────────────────────────────┐
│         Phase 4 데이터 흐름          │
├─────────────────────────────────────┤
│                                     │
│  [SearchResult] → (Pandas) → [CSV]  │
│                                     │
└─────────────────────────────────────┘
```

---

# Phase 5: UI 컴포넌트

## 이 프롬프트의 역할
- Streamlit의 개별 기능을 담당하는 독립적인 UI 함수 생성
- 생성된 파일: `components/search_form.py`, `components/sidebar.py`, `components/result_section.py`, `components/loading.py`

## 학습 목표
- Streamlit의 위젯(Slider, Selectbox, Expander) 활용법 익히기
- 컨텍스트 매니저(`with`)를 이용한 로딩 상태 구현 방법 이해

## 이해를 위한 핵심 개념

### 5.1 컴포넌트 기반 UI
UI를 작은 기능 단위로 함수화하여 관리합니다. 이는 메인 앱 코드를 깔끔하게 유지하고 재사용성을 높여줍니다.

### 5.2 로딩 가시성 (Spinner)
장시간 소요되는 API 연동(검색, 요약) 중 사용자에게 진행 상황을 알려주어 이탈을 방지합니다.

## 주요 코드 인용

### `components/loading.py` - 커스텀 로딩 매니저
```python
# components/loading.py:4-8
@contextmanager
def show_loading(message: str):
    """st.spinner를 이용한 로딩 상태 표시 컨텍스트 매니저"""
    with st.spinner(message):
        yield
```

**코드 설명:**
- `@contextmanager`: `with` 구문을 통해 로딩바를 간편하게 켜고 끌 수 있게 합니다.

## 데이터 흐름에서의 역할

```
┌─────────────────────────────────────┐
│         Phase 5 데이터 흐름          │
├─────────────────────────────────────┤
│                                     │
│  [Action] → (UI Function) → [Visual] │
│                                     │
└─────────────────────────────────────┘
```

---

# Phase 6: 메인 앱 통합

## 이 프롬프트의 역할
- 앞서 만든 컴포넌트와 서비스를 한데 모아 전체 앱의 흐름(Flow)을 구성
- 생성된 파일: `app.py`

## 학습 목표
- `st.session_state`를 활용한 앱 상태(State) 관리 기법 이해
- 사용자 선택에 따른 조건부 렌더링 및 `st.rerun()` 활용 학습

## 이해를 위한 핵심 개념

### 6.1 세션 상태 (Session State)
Streamlit은 코드 변경 시 전체가 재실행됩니다. 이때 사용자가 방금 검색한 결과나 현재 선택한 페이지 모드를 유지하기 위해 `session_state`를 사용합니다.

### 6.2 모드 전환 패턴
"새로운 검색" 모드와 "검색 기록 조회" 모드를 변수로 관리하여 하나의 화면에서 서로 다른 내용을 보여줍니다.

## 주요 코드 인용

### `app.py` - 상태 기반 모드 전환
```python
# app.py:32-37
    # 세션 상태 초기화
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "new_search"
    if "selected_key" not in st.session_state:
        st.session_state.selected_key = None
```

## 데이터 흐름에서의 역할

```
┌─────────────────────────────────────┐
│         Phase 6 데이터 흐름          │
├─────────────────────────────────────┤
│                                     │
│  [User Action] → [State Change]     │
│       ↓              ↓              │
│  [Service/Repo] → [UI Display]      │
│                                     │
└─────────────────────────────────────┘
```

---

# Phase 7: 에러 핸들링 강화 및 마무리

## 이 프롬프트의 역할
- 앱의 안정성을 높이고 사용자 환경을 최종적으로 정리하는 작업
- 생성된 파일: `README.md`, 각 파일의 Docstring 추가 및 리팩토링

## 학습 목표
- 상세한 HTTP 에러 코드별(401, 429, 5xx) 맞춤 안내 메시지 구현
- 네트워크 타임아웃 및 재시도 로직을 통한 견고한 시스템 구축

## 이해를 위한 핵심 개념

### 7.1 방어적 프로그래밍
API 서버가 응답하지 않거나 API 키가 만료된 상황에서도 앱이 멈추지 않고 적절한 한글 안내를 제공하도록 합니다.

### 7.2 문서화 (README)
다른 사용자나 개발자가 프로젝트를 쉽고 정확하게 실행할 수 있도록 안내하는 가이드라인을 작성합니다.

## 주요 코드 인용

### `services/search_service.py` - 재시도 및 상세 에러 처리
```python
# services/search_service.py:74-88
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code == 401:
                raise AppError("tavily_api_key_invalid")
            elif status_code == 429:
                raise AppError("tavily_limit_exceeded")
            
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue
```

---

# 전체 데이터 흐름

## 시나리오 1: 새로운 키워드 검색 및 요약

```
키워드 입력 (Search Form)
    │
    ▼
입력값 검증 및 전처리 (utils.input_handler)
    │
    ▼
뉴스 검색 (Tavily API - services.search_service)
    │
    ▼
기사 요약 (Gemini AI - services.ai_service)
    │
    ▼
결과 저장 (CSV 파일 - repositories.search_repository)
    │
    ▼
화면 출력 (Main Area - components.result_section)
```

## 시나리오 2: 과거 검색 기록 조회

```
사이드바에서 히스토리 선택 (Sidebar selectbox)
    │
    ▼
search_key 기반 데이터 로드 (repositories.search_repository)
    │
    ▼
불러온 데이터로 SearchResult 객체 복원 (domain.search_result)
    │
    ▼
과거 결과 화면 렌더링 (app.py - Main Area)
```

## 폴더 구조 요약

```
initial_version/
├── config/ setting.py  ← [Phase 1] 환경변수 관리
├── domain/ models      ← [Phase 2] 핵심 데이터 구조
├── services/ api_logic ← [Phase 3] 검색 및 AI 통신
├── repositories/ csv   ← [Phase 4] 파일 입출력 관리
├── components/ ui      ← [Phase 5] 조립식 UI 부품
├── app.py              ← [Phase 6] 전체 앱 조립 및 실행
└── README.md           ← [Phase 7] 사용 설명 및 가이드
```

---

## 학습 체크리스트

### Phase 1
- [ ] uv를 이용해 가상환경을 구축할 수 있는가?
- [ ] Settings 클래스가 환경변수 누락 시 어떤 방식으로 경고를 주는가?

### Phase 2
- [ ] dataclass를 사용하는 이유가 무엇인가?
- [ ] search_key에 타임스탬프를 포함하는 이유는 무엇인가?

### Phase 3
- [ ] 외부 API 응답 데이터를 도메인 모델로 매핑하는 과정이 이해되는가?
- [ ] AppError라는 커스텀 예외를 사용하면 유지보수 측면에서 어떤 장점이 있는가?

### Phase 4
- [ ] Pandas의 CSV 읽기/쓰기 모드(`pd.concat`)가 이해되는가?
- [ ] 파일 입출력 시 한글 깨짐 방지를 위한 조치는 무엇인가?

### Phase 5
- [ ] Streamlit의 사이드바와 메인 영역을 어떻게 구분하여 코딩하는가?
- [ ] 로딩바를 `with` 구문으로 관리하는 이유는 무엇인가?

### Phase 6
- [ ] `st.session_state`가 필요한 구체적인 시나리오를 설명할 수 있는가?
- [ ] `st.rerun()`은 화면을 언제 갱신시키는가?

### Phase 7
- [ ] API 키 만료 같은 상황을 테스트하기 위해 어떤 방식을 사용하는가?
- [ ] Docstring이 코드 이해도에 어떤 영향을 주는가?

---
**학습 가이드 작성을 완료했습니다. 이 문서가 당신의 프로젝트 마스터를 위한 좋은 나침반이 되길 바랍니다!**
