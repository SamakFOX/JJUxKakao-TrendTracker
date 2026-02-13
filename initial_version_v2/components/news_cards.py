import streamlit as st
from typing import List, Dict
import re

def strip_markdown(text: str) -> str:
    if not text:
        return ""
    # 헤더 기호 제거
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    # 굵게/기울임/코드블록 일부 제거
    text = text.replace("**", "").replace("__", "").replace("`", "")
    return text

def render_trending_news_cards(news_list: List[Dict], key_prefix: str = "trending"):
    """트렌딩 뉴스를 4열 그리드 카드로 렌더링합니다."""
    if not news_list:
        st.info("현재 표시할 수 있는 트렌딩 뉴스가 없습니다.")
        return

    st.subheader("📰 Google 트렌드")

    rows = [news_list[i:i + 4] for i in range(0, len(news_list), 4)]

    global_idx = 0
    for row in rows:
        cols = st.columns(4)
        for col_i, news in enumerate(row):
            with cols[col_i]:
                with st.container(border=True):
                    title = news.get("title", "")
                    if len(title) > 50:
                        title = title[:47] + "..."
                    title = strip_markdown(title)
                    st.markdown(f"<div class='news-card-title'>{title}</div>", unsafe_allow_html=True)

                    st.markdown(f"<div class='news-card-source'>📍 {news['source']}</div>", unsafe_allow_html=True)

                    snippet = news.get("snippet", "")
                    if len(snippet) > 60:
                        snippet = snippet[:57] + "..."
                    snippet = strip_markdown(snippet)
                    st.markdown(f"<div class='news-card-snippet'>{snippet}</div>", unsafe_allow_html=True)

                    # ✅ key가 row를 넘어도 유니크해짐
                    btn_key = f"{key_prefix}_news_btn_{global_idx}"

                    if st.button("내용 보기", key=btn_key, width="stretch"):
                        st.session_state.active_popup_type = "news"
                        st.session_state.active_popup_data = news
                        st.rerun()

                    global_idx += 1
