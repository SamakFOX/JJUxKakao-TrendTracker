import streamlit as st
from typing import List

def render_trending_section(keywords: List[str]):
    """
    실시간 인기 검색어 섹션을 렌더링합니다. (Phase 10: 칩 형태 2줄 배치)
    """
    st.subheader("🔥 실시간 인기 검색어")
    
    if not keywords:
        st.info("아직 검색 기록이 없습니다. 키워드를 입력해 첫 검색을 시작해보세요!")
        return

    # 최대 12개, 한 줄에 6개씩 배치
    max_keywords = keywords[:12]
    rows = [max_keywords[i:i + 6] for i in range(0, len(max_keywords), 6)]
    
    for row in rows:
        cols = st.columns(6) # 6컬럼 고정으로 정렬 유지
        for i, keyword in enumerate(row):
            if cols[i].button(f"{keyword}", key=f"trend_{keyword}", width="stretch"):
                # 클릭 시 검색어로 예약
                st.session_state.pending_keyword = keyword
                st.rerun()
