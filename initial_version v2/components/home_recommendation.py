import streamlit as st
from .youtube_cards import render_youtube_cards
from .news_cards import render_trending_news_cards

def render_home_recommendations(youtube_videos: list, trending_news: list):
    """홈 화면 하단의 오늘의 추천 콘텐츠 영역을 렌더링합니다."""
    st.divider()
    st.header("📌 오늘의 추천 콘텐츠")
    
    # 두 섹션을 수직으로 배치
    render_youtube_cards(youtube_videos)
    st.write("") # 간격
    render_trending_news_cards(trending_news)
