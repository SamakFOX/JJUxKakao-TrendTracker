# TrendTracker (TrendTracker v1.0)

키워드로 구글 뉴스를 검색하고 Gemini AI를 통해 핵심 내용을 요약해주는 웹 애플리케이션입니다.

## ✨ 주요 기능
- **실시간 뉴스 검색**: Tavily API를 연동하여 최신 테크/뉴스 트렌드를 검색합니다.
- **AI 핵심 요약**: Google Gemini API를 사용하여 검색된 기사들을 한국어로 요약합니다.
- **히스토리 관리**: 로컬 CSV 파일에 검색 기록을 자동 저장하고, 다시 불러올 수 있습니다.
- **데이터 내보내기**: 전체 검색 기록을 CSV 파일로 다운로드할 수 있습니다.
- **사용자 친화적 UI**: Streamlit을 활용한 직관적이고 반응형인 인터페이스를 제공합니다.

## 🛠️ 폴더 구조
```
initial_version/
├── app.py                  # 메인 실행 파일
├── config/
│   └── settings.py         # 환경 변수 및 설정 관리
├── domain/
│   ├── news_article.py     # 뉴스 기사 데이터 모델
│   └── search_result.py    # 검색 결과 데이터 모델
├── services/
│   ├── search_service.py   # Tavily 뉴스 검색 서비스
│   └── ai_service.py       # Gemini AI 요약 서비스
├── repositories/
│   └── search_repository.py # CSV 데이터 입출력 리포지토리
├── components/
│   ├── search_form.py      # 메인 검색 폼 컴포넌트
│   ├── sidebar.py          # 사이드바 컴포넌트
│   ├── result_section.py   # 결과 표시 섹션 컴포넌트
│   └── loading.py          # 로딩 상태 표시 컴포넌트
├── utils/
│   ├── exceptions.py       # 커스텀 예외 정의
│   ├── error_handler.py    # 통합 에러 핸들링
│   ├── key_generator.py    # 고유 키 생성 유틸리티
│   └── input_handler.py    # 입력값 전처리 유틸리티
├── data/
│   └── search_history.csv  # 검색 기록 저장소 (자동 생성)
├── .env                    # API 키 설정 파일 (사용자 생성 필요)
├── .env.example            # 환경 변수 템플릿
└── pyproject.toml          # 의존성 및 프로젝트 설정
```

## 🚀 시작하기

### 1. 환경 준비
이 프로젝트는 `uv` 패키지 매니저를 권장합니다.
- **Windows**: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- **macOS/Linux**: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 2. 의존성 설치
```bash
uv sync
```

### 3. API 키 설정
프로젝트 루트에 `.env` 파일을 생성하고 다음 API 키를 입력하세요.
```text
TAVILY_API_KEY=your_tavily_api_key
GEMINI_API_KEY=your_gemini_api_key
CSV_PATH=data/search_history.csv
SEARCH_DOMAINS=techcrunch.com,theverge.com,zdnet.com
```

- **Tavily API**: [tavily.com](https://tavily.com/)에서 무료 키 발급 가능
- **Gemini API**: [Google AI Studio](https://aistudio.google.com/)에서 무료 키 발급 가능

### 4. 실행
```bash
uv run streamlit run app.py
```

## ⚠️ 주의사항
- **데이터 저장**: 검색 기록은 로컬의 `data/search_history.csv` 파일에 물리적으로 저장됩니다. 파일을 삭제하면 이전 기록이 사라집니다.
- **API 한도**: 무료 티어 사용 시 분당/월간 요청 횟수 제한이 있을 수 있으니 에러 메시지를 확인해 주세요.

---
© 2026 TrendTracker 팀.
