# app.py
import streamlit as st
from datetime import datetime

from config.settings import settings
from repositories.search_repository import SearchRepository
from services.search_service import search_news
from services.ai_service import summarize_news_with_keywords
from services.youtube_service import get_trending_videos
from services.trending_news_service import get_home_trending_news

from utils.exceptions import AppError
from utils.error_handler import handle_error
from utils.key_generator import generate_search_key
from domain.search_result import SearchResult

from components.search_form import render_search_form
from components.result_section import render_summary, render_news_list, render_related_keywords
from components.trending_section import render_trending_section
from components.home_recommendation import render_home_recommendations
from components.popup_viewer import render_popups
from components.loading import show_loading
from components.top_nav import render_top_nav, render_nav_panels


# =========================================================
# 0) 페이지 설정 (⚠️ 반드시 st.* 출력 전에 제일 먼저)
# =========================================================
st.set_page_config(
    page_title="TrendTracker",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# 1) UI 패치: Streamlit 기본 상단/메뉴 숨김 + 다크 배경 고정
#    (Streamlit Cloud 배포에서 "상단바가 겹쳐 보임" / 배경이 하얘짐 방지)
# =========================================================
st.markdown(
    """
<style>
/* ===== Streamlit 기본 UI 숨김 ===== */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }

/* 상단 여백 튜닝(배포 환경에서 위가 뜨는 느낌 줄이기) */
div.block-container { padding-top: 1.1rem !important; }

/* 입력창 톤 보정 */
div[data-baseweb="input"] input {
  background: rgba(255,255,255,0.06) !important;
  color: #fafafa !important;
}

/* ===== 카카오 스타일 GNB 완벽 재현 ===== */
.tt-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 72px;
  background-color: #0e1117; /* 다크 테마 유지 */
  border-bottom: 1px solid rgba(255,255,255,0.05);
  position: relative;
  width: 100%;
}

.tt-brand {
  position: absolute;
  left: 24px;
  font-weight: 800;
  font-size: 20px;
  color: #ffffff;
  letter-spacing: -0.8px;
  text-decoration: none;
}

.tt-menu-container {
  display: flex;
  gap: 48px; /* 메뉴 간 촘촘한 간격 */
  align-items: center;
}
</style>
""",
    unsafe_allow_html=True
)

# =========================================================
# 2) 상단 네비 모달
# =========================================================
def _open_nav_modal(name: str):
    st.session_state.nav_modal = name

def _close_nav_modal():
    st.session_state.nav_modal = None

@st.dialog("📖 사용법")
def _dlg_usage():
    st.markdown(
        """
1. **키워드 입력**: 메인 화면에서 검색어를 입력합니다.  
2. **조건(선택)**: 포함(AND) / 제외(NOT) / 기간 / 도메인 필터를 조정합니다.  
3. **뉴스 검색**: 결과와 AI 요약/연관 키워드를 확인합니다.  
4. **검색기록**: 상단의 ‘검색기록’에서 과거 결과를 다시 볼 수 있습니다.  
        """
    )
    if st.button("닫기", width="stretch", key="btn_close_usage"):
        _close_nav_modal()
        st.rerun()

@st.dialog("📊 API 한도")
def _dlg_api_limit():
    st.markdown(
        """
- **Tavily**: 무료 플랜 기준 월 요청 수 제한이 있을 수 있습니다.  
- **Gemini**: 무료 티어 기준 분당 요청/일일 요청 제한이 있을 수 있습니다.  
- 실제 한도는 플랜/키 설정에 따라 달라질 수 있습니다.
        """
    )
    if st.button("닫기", width="stretch", key="btn_close_api"):
        _close_nav_modal()
        st.rerun()

@st.dialog("💾 데이터 저장 안내")
def _dlg_storage():
    st.info(
        "- 검색 기록은 CSV 파일에 저장됩니다.\n"
        "- CSV를 삭제하면 과거 기록이 사라집니다.\n"
        "- 중요한 데이터는 주기적으로 다운로드를 권장합니다."
    )
    if st.button("닫기", width="stretch", key="btn_close_storage"):
        _close_nav_modal()
        st.rerun()

@st.dialog("📜 검색 기록")
def _dlg_history(repository: SearchRepository):
    search_keys = repository.get_all_keys()
    if not search_keys:
        st.info("저장된 검색 기록이 없습니다.")
        if st.button("닫기", width="stretch"):
            _close_nav_modal()
            st.rerun()
        return

    options = []
    key_map = {}
    for key in search_keys:
        try:
            keyword = key.rsplit("-", 1)[0]
            ts_str = key.rsplit("-", 1)[1]
            dt = datetime.strptime(ts_str, "%Y%m%d%H%M")
            label = f"{keyword} ({dt.strftime('%Y-%m-%d %H:%M')})"
        except:
            label = key
        options.append(label)
        key_map[label] = key

    selected = st.selectbox("기록 선택", options=options, index=None, placeholder="과거 결과 선택...")
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        if st.button("선택한 기록 열기", width="stretch", disabled=(selected is None)):
            st.session_state.current_mode = "history"
            st.session_state.selected_key = key_map[selected]
            st.session_state.last_result = None
            _close_nav_modal()
            st.rerun()

    with col2:
        csv_data = repository.get_all_as_csv()
        st.download_button(
            label="CSV 다운로드",
            data=csv_data,
            file_name=f"trendtracker_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            width="stretch",
        )

    if st.button("닫기", width="stretch"):
        _close_nav_modal()
        st.rerun()

def _render_nav_modals(repository: SearchRepository):
    modal = st.session_state.get("nav_modal")
    if modal == "usage":
        _dlg_usage()
    elif modal == "api":
        _dlg_api_limit()
    elif modal == "storage":
        _dlg_storage()
    elif modal == "history":
        _dlg_history(repository)

def render_top_nav(repository: SearchRepository):
    """
    상단 네비게이션 바를 렌더링합니다. (카카오 스타일 중앙 밀집형)
    """
    if "nav_modal" not in st.session_state:
        st.session_state.nav_modal = None
    
    # GNB 시작
    st.markdown('<div class="tt-nav">', unsafe_allow_html=True)
    st.markdown('<div class="tt-brand">TrendTracker</div>', unsafe_allow_html=True)
    
    # 컨테이너와 컬럼을 조합하여 중앙 배치를 정밀하게 제어
    # 양 끝 여백을 넓게 주어 버튼들이 가운데로 모이게 함
    _, center_col, _ = st.columns([0.35, 0.3, 0.35])
    
    with center_col:
        st.markdown('<div class="tt-menu-container">', unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns([1, 1, 1, 1])
        
        with m1:
            st.markdown('<div class="tt-menu-btn">', unsafe_allow_html=True)
            if st.button("사용법", key="nav_usage"):
                _open_nav_modal("usage")
            st.markdown("</div>", unsafe_allow_html=True)

        with m2:
            st.markdown('<div class="tt-menu-btn">', unsafe_allow_html=True)
            if st.button("API 한도", key="nav_api"):
                _open_nav_modal("api")
            st.markdown("</div>", unsafe_allow_html=True)

        with m3:
            st.markdown('<div class="tt-menu-btn">', unsafe_allow_html=True)
            if st.button("데이터 안내", key="nav_storage"):
                _open_nav_modal("storage")
            st.markdown("</div>", unsafe_allow_html=True)

        with m4:
            st.markdown('<div class="tt-menu-btn">', unsafe_allow_html=True)
            if st.button("검색기록", key="nav_history"):
                _open_nav_modal("history")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True) # tt-menu-container end

    st.markdown("</div>", unsafe_allow_html=True) # tt-nav end

    # 모달 렌더
    _render_nav_modals(repository)


# =========================================================
# 3) main()
# =========================================================
def main():
    repository = SearchRepository(settings.CSV_PATH)

    # 세션 상태 초기화
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "new_search"
    if "selected_key" not in st.session_state:
        st.session_state.selected_key = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    # Phase 9 & 10 세션 상태
    if "search_main_raw" not in st.session_state: st.session_state.search_main_raw = ""
    if "search_and_raw" not in st.session_state: st.session_state.search_and_raw = ""
    if "search_not_raw" not in st.session_state: st.session_state.search_not_raw = ""
    if "show_advanced_filters" not in st.session_state: st.session_state.show_advanced_filters = False
    if "date_filter_mode" not in st.session_state: st.session_state.date_filter_mode = "24h"
    if "selected_domain_categories" not in st.session_state: st.session_state.selected_domain_categories = []
    if "pending_keyword" not in st.session_state: st.session_state.pending_keyword = None

    # 팝업 상태
    if "active_popup_type" not in st.session_state: st.session_state.active_popup_type = None
    if "active_popup_data" not in st.session_state: st.session_state.active_popup_data = None

    # 홈 추천 데이터 캐시
    if "home_youtube_videos" not in st.session_state: st.session_state.home_youtube_videos = None
    if "home_trending_news" not in st.session_state: st.session_state.home_trending_news = None

    if st.session_state.home_youtube_videos is None:
        st.session_state.home_youtube_videos = get_trending_videos(8)
    if st.session_state.home_trending_news is None:
        st.session_state.home_trending_news = get_home_trending_news(repository, 8)

    # ✅ 상단 네비(사이드바 대체)
    render_top_nav(repository)

    # ✅ 팝업(유튜브/뉴스)
    render_popups()

    # 1) 새 검색 모드
    if st.session_state.current_mode == "new_search":
        trending_keywords = repository.get_trending_keywords(hours=24, limit=12)
        render_trending_section(trending_keywords)

        st.divider()
        st.title("🔍 새로운 트렌드 검색")

        filters = render_search_form()
        num_results = st.session_state.get("num_results", 5)

        if filters:
            try:
                with show_loading("🔍 뉴스를 검색하고 있습니다..."):
                    articles = search_news(filters, num_results)

                if not articles:
                    st.info("검색 결과가 없습니다. 다른 조건으로 시도해보세요.")
                else:
                    with show_loading("🤖 AI가 핵심 내용을 요약하고 있습니다..."):
                        ai_output = summarize_news_with_keywords(articles)

                    keyword_display = ",".join(filters.main_terms)
                    search_key = generate_search_key(keyword_display)
                    search_time = datetime.now()

                    result = SearchResult(
                        search_key=search_key,
                        search_time=search_time,
                        keyword=keyword_display,
                        articles=articles,
                        ai_summary=ai_output.summary,
                        related_keywords=ai_output.related_keywords,
                    )

                    with show_loading("💾 결과를 저장하고 있습니다..."):
                        if repository.save(result):
                            st.session_state.last_result = result
                            st.success(f"'{keyword_display}' 검색 완료! {len(articles)}건의 뉴스를 찾아서 저장했습니다.")
                            st.rerun()
                        else:
                            handle_error("file_error")

            except AppError as e:
                handle_error(e.error_type)
            except Exception as e:
                st.error(f"애플리케이션 오류가 발생했습니다: {e}")

        # 결과 표시
        if st.session_state.last_result:
            res = st.session_state.last_result
            render_summary(f"'{res.keyword}' 최신 트렌드 요약", res.ai_summary)
            render_related_keywords(res.related_keywords)
            render_news_list(res.articles)
        else:
            render_home_recommendations(
                st.session_state.home_youtube_videos,
                st.session_state.home_trending_news
            )

    # 2) 기록 조회 모드
    elif st.session_state.current_mode == "history" and st.session_state.selected_key:
        st.title("📜 과거 검색 기록")

        col1, col2 = st.columns([0.85, 0.15], vertical_alignment="center")
        with col2:
            if st.button("➕ 새 검색", width="stretch"):
                st.session_state.current_mode = "new_search"
                st.session_state.selected_key = None
                st.session_state.last_result = None
                st.rerun()

        with show_loading("기록을 불러오고 있습니다..."):
            result = repository.find_by_key(st.session_state.selected_key)

        if result:
            render_summary(
                f"검색 기록: {result.keyword} ({result.search_time.strftime('%Y-%m-%d %H:%M')})",
                result.ai_summary
            )
            render_related_keywords(result.related_keywords)
            render_news_list(result.articles)
        else:
            st.error("해당 기록을 찾을 수 없거나 불러오는 중 오류가 발생했습니다.")
            if st.button("목록으로 돌아가기"):
                st.session_state.current_mode = "new_search"
                st.session_state.selected_key = None
                st.rerun()


if __name__ == "__main__":
    main()
