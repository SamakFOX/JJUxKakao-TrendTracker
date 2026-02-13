from typing import Optional
import streamlit as st
from datetime import date
from utils.query_builder import parse_terms
from domain.search_filters import SearchFilters
from components.chips import render_category_chips, get_selected_domains
from config.settings import settings


def _close_popup():
    st.session_state.active_popup_type = None
    st.session_state.active_popup_data = None


def _trigger_search():
    """엔터(Enter) 입력 시 호출: 검색 실행 플래그만 올림"""
    st.session_state._do_search = True


def render_search_form() -> Optional[SearchFilters]:
    """
    고급 필터를 포함한 검색 폼을 렌더링합니다.
    - Enter(엔터)로 검색 가능 (text_input on_change)
    - 검색어가 비어있으면 검색 실행되지 않음
    - 검색창 - 조건 - 뉴스검색을 한 줄로 배치
    """

    # 엔터 검색 플래그 초기화
    if "_do_search" not in st.session_state:
        st.session_state._do_search = False

    # pending_keyword 처리(검색어 주입)
    initial_val = st.session_state.get("pending_keyword", "")
    if initial_val:
        st.session_state.search_main_raw = initial_val
        st.session_state.pending_keyword = None
        # 주입된 경우 자동 검색하고 싶으면 True로 올려도 됨
        # st.session_state._do_search = True

    # 상단: 검색창 - 조건 - 뉴스검색 (한 줄)
    col_input, col_opt, col_search = st.columns(
        [0.74, 0.13, 0.13],
        vertical_alignment="bottom"
    )

    with col_input:
        st.text_input(
            "검색어 입력",
            value=st.session_state.get("search_main_raw", ""),
            placeholder="예: 고양이, 강아지 (여러 단어는 쉼표로 구분)",
            key="search_main_raw",
            label_visibility="collapsed",
            on_change=_trigger_search  # ✅ 엔터로 검색 트리거
        )

    with col_opt:
        if st.button("⚙️ 조건", key="btn_toggle_filters", width="stretch"):
            _close_popup()
            st.session_state.show_advanced_filters = not st.session_state.get("show_advanced_filters", False)
            st.rerun()

    with col_search:
        if st.button("🔍 뉴스 검색", key="btn_execute_search", width="stretch", type="primary"):
            st.session_state._do_search = True

    # 고급 조건 패널
    if st.session_state.get("show_advanced_filters", False):
        with st.expander("고급 검색 설정", expanded=True):
            col_and, col_not = st.columns(2)
            with col_and:
                st.text_input(
                    "포함(AND)",
                    value=st.session_state.get("search_and_raw", ""),
                    placeholder="반드시 포함할 단어 (쉼표로 여러 개 입력 가능)",
                    help="여기에 입력한 단어는 기사에 반드시 포함되어야 합니다.",
                    key="search_and_raw"
                )
            with col_not:
                st.text_input(
                    "제외(NOT)",
                    value=st.session_state.get("search_not_raw", ""),
                    placeholder="제외할 단어 (쉼표로 여러 개 입력 가능)",
                    help="여기에 입력한 단어가 포함된 기사는 제외됩니다.",
                    key="search_not_raw"
                )

            st.divider()

            st.slider(
                "검색 결과 개수",
                min_value=1,
                max_value=10,
                value=st.session_state.get("num_results", 5),
                step=1,
                key="num_results",
                help="가져올 뉴스 기사의 최대 개수를 설정합니다."
            )

            st.divider()

            col_date_mode, col_date_custom = st.columns([0.4, 0.6])
            with col_date_mode:
                date_mode = st.radio(
                    "검색 기간",
                    options=["24h", "7d", "30d", "custom"],
                    format_func=lambda x: {
                        "24h": "최근 24시간",
                        "7d": "최근 7일",
                        "30d": "최근 30일",
                        "custom": "직접 선택"
                    }[x],
                    index=["24h", "7d", "30d", "custom"].index(
                        st.session_state.get("date_filter_mode", "24h")
                    ),
                    key="date_filter_mode",
                    horizontal=True
                )

            with col_date_custom:
                if date_mode == "custom":
                    st.date_input(
                        "기간 지정",
                        value=(
                            st.session_state.get("date_custom_start", date.today()),
                            st.session_state.get("date_custom_end", date.today())
                        ),
                        key="date_range_input"
                    )

            st.divider()

            st.session_state.selected_domain_categories = render_category_chips(
                settings.DOMAIN_CATEGORIES,
                st.session_state.get("selected_domain_categories", [])
            )

    # ✅ 검색 실행: 버튼 클릭 또는 엔터
    if st.session_state._do_search:
        st.session_state._do_search = False  # 플래그 즉시 내리기(중복 실행 방지)

        raw = (st.session_state.get("search_main_raw") or "").strip()
        if not raw:
            st.warning("검색어를 입력해주세요.")
            return None

        # custom 날짜 처리
        custom_start = None
        custom_end = None
        if st.session_state.get("date_filter_mode") == "custom":
            date_range = st.session_state.get("date_range_input")
            if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                custom_start, custom_end = date_range

        filters = SearchFilters(
            main_terms=parse_terms(raw),
            and_terms=parse_terms(st.session_state.get("search_and_raw", "")),
            not_terms=parse_terms(st.session_state.get("search_not_raw", "")),
            date_filter_mode=st.session_state.get("date_filter_mode", "24h"),
            custom_start=custom_start,
            custom_end=custom_end,
            include_domains=get_selected_domains(
                settings.DOMAIN_CATEGORIES,
                st.session_state.get("selected_domain_categories", [])
            )
        )
        return filters

    return None
