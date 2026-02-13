import streamlit as st
import html


@st.dialog("📺 인기 유튜브 영상")
def show_youtube_popup(video_data: dict):
    video_id = video_data.get("id")
    title = video_data.get("title", "")

    st.markdown(f"### {title}")

    # 🔥 가로형(16:9) 고정 컨테이너
    st.components.v1.html(
        f"""
        <style>
        .video-wrapper {{
            position: relative;
            width: 100%;
            max-width: 960px;
            margin: 0 auto;
            aspect-ratio: 16 / 9;
            background: black;
        }}
        .video-wrapper iframe {{
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            border-radius: 12px;
        }}
        </style>

        <div class="video-wrapper">
            <iframe
                src="https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0"
                frameborder="0"
                allow="autoplay; encrypted-media; picture-in-picture"
                allowfullscreen>
            </iframe>
        </div>
        """,
        height=560   # 👉 팝업 자체 높이도 키움 (기존보다 약 1.5배)
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("닫기", width="stretch"):
        st.session_state.active_popup_type = None
        st.session_state.active_popup_data = None
        st.rerun()


@st.dialog("📰 트렌딩 뉴스")
def show_news_popup(news_data: dict):
    """뉴스 내용을 팝업으로 보여줍니다. (본문만 스크롤)"""
    news_data = news_data or {}

    title = news_data.get("title", "뉴스")
    snippet = news_data.get("snippet", "")
    url = news_data.get("url", "")
    pub_date = news_data.get("pub_date", "")
    source = news_data.get("source", "")

    safe_title = html.escape(title)
    safe_source = html.escape(source)
    safe_pub_date = html.escape(pub_date)
    safe_url = html.escape(url)
    safe_snippet = html.escape(snippet)

    # ✅ 상단 영역(항상 보이게)
    top_l, top_r = st.columns([0.85, 0.15], vertical_alignment="center")
    with top_l:
        st.markdown(f"### {safe_title}")
        if source or pub_date:
            st.caption(f"{safe_source} | {safe_pub_date}")
    with top_r:
        if st.button("닫기", width="stretch", key="news_popup_close_top"):
            st.session_state.active_popup_type = None
            st.session_state.active_popup_data = None
            st.rerun()

    if url:
        st.markdown(f"[🔗 새 탭에서 기사 보기]({safe_url})")

    st.divider()

    # ✅ 본문만 스크롤되도록: 고정 높이 + overflow
    # - height는 화면에 맞게 적당히 (너무 크면 잘림)
    # - 모바일/작은 화면에서도 대응하려면 60vh 같은 뷰포트 단위 추천
    st.markdown(
        f"""
        <style>
          .news-scroll {{
            height: 60vh;
            overflow-y: auto;
            padding-right: 8px;
            white-space: pre-wrap;
            line-height: 1.6;
            font-size: 0.95rem;
          }}
          /* 스크롤바 살짝 이쁘게 (선택) */
          .news-scroll::-webkit-scrollbar {{
            width: 10px;
          }}
          .news-scroll::-webkit-scrollbar-thumb {{
            background: rgba(255,255,255,0.15);
            border-radius: 8px;
          }}
        </style>

        <div class="news-scroll">
          {safe_snippet}
        </div>
        """,
        unsafe_allow_html=True
    )

    if url:
        st.markdown(f"#### [🔗 새 탭에서 기사 보기]({url})")
    else:
        st.info("기사 링크가 없어 새 탭 열기를 제공할 수 없습니다.")


def render_popups():
    """세션 상태에 따라 팝업을 호출합니다."""
    popup_type = st.session_state.get("active_popup_type")

    if popup_type == "youtube":
        show_youtube_popup(st.session_state.get("active_popup_data") or {})
    elif popup_type == "news":
        show_news_popup(st.session_state.get("active_popup_data") or {})
