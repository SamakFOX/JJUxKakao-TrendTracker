import streamlit as st
from typing import List, Dict
import math
def _close_popup():
    st.session_state.active_popup_type = None
    st.session_state.active_popup_data = None

def render_youtube_cards(videos: List[Dict], key_prefix: str = "yt"):
    """유튜브 영상을 1줄 4개 + 페이지네이션으로 렌더링합니다."""
    if not videos:
        st.info("현재 표시할 수 있는 유튜브 영상이 없습니다.")
        return

    # 페이지 상태
    if "youtube_page" not in st.session_state:
        st.session_state.youtube_page = 0

    per_page = 4
    total_pages = max(1, math.ceil(len(videos) / per_page))
    page = min(st.session_state.youtube_page, total_pages - 1)

    # 헤더 + 우측 상단 페이지 버튼
    hcol1, hcol2 = st.columns([0.75, 0.25], vertical_alignment="center")
    with hcol1:
        st.subheader("📺 인기 유튜브 영상")
        st.caption(f"{page+1} / {total_pages} 페이지")
    with hcol2:
        b1, b2 = st.columns(2)
        with b1:
            prev_disabled = page <= 0
            if st.button("◀ 이전", key=f"{key_prefix}_prev", disabled=prev_disabled, width="stretch"):
                _close_popup()
                st.session_state.youtube_page = max(0, page - 1)
                st.rerun()
        with b2:
            next_disabled = page >= total_pages - 1
            if st.button("다음 ▶", key=f"{key_prefix}_next", disabled=next_disabled, width="stretch"):
                _close_popup()
                st.session_state.youtube_page = min(total_pages - 1, page + 1)
                st.rerun()

    # 현재 페이지 데이터 슬라이스 (4개)
    start = page * per_page
    end = start + per_page
    page_items = videos[start:end]

    # ✅ 1줄 4개 고정
    cols = st.columns(4)
    for idx in range(4):
        with cols[idx]:
            if idx >= len(page_items):
                st.empty()
                continue

            video = page_items[idx]
            with st.container(border=True):
                # 썸네일만 노출
                thumb = video.get("thumbnail", "")
                if thumb:
                    st.image(thumb, width="stretch")

                # 재생 버튼
                vid = video.get("id", "")
                btn_key = f"{key_prefix}_play_{page}_{idx}_{vid}"
                if st.button("▶ 재생", key=btn_key, width="stretch"):
                    st.session_state.active_popup_type = "youtube"
                    st.session_state.active_popup_data = video
                    st.rerun()
