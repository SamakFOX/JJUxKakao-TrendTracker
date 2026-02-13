from typing import List
import streamlit as st
from domain.news_article import NewsArticle

def render_summary(title: str, summary: str):
    """AI 요약 결과를 렌더링합니다."""
    st.markdown("---")
    st.subheader(f"🤖 {title}")
    
    # AI 요약 내용을 강조된 박스에 표시
    st.info(summary)

def render_news_list(articles: List[NewsArticle]):
    """뉴스 기사 리스트를 각 기사별 expander로 렌더링합니다."""
    st.markdown("---")
    st.subheader("📰 최신 관련 뉴스")
    
    if not articles:
        st.write("검색된 뉴스가 없습니다.")
        return
        
    for i, article in enumerate(articles, 1):
        # 발행일 정보가 있으면 제목 뒤에 표시
        date_str = f" ({article.pub_date})" if article.pub_date else ""
        expander_title = f"{i}. {article.title}{date_str}"
        
        with st.expander(expander_title):
            if article.pub_date:
                st.markdown(f"**📅 발행일:** {article.pub_date}")
            
            # 스니펫 (내용 요약)
            st.write(article.snippet)
            
            # 원문 링크
            if article.url:
                st.markdown(f"[🔗 기사 원문 보기]({article.url})")
            else:
                st.write("(URL 정보 없음)")

def render_related_keywords(keywords: List[str]):
    """
    연관 키워드를 가로 가변 버튼 리스트로 렌더링합니다.
    """
    if not keywords:
        return
        
    st.subheader("🔁 연관 키워드")
    
    # 5개씩 끊어서 출력
    rows = [keywords[i:i + 5] for i in range(0, len(keywords), 5)]
    for row_idx, row in enumerate(rows):
        cols = st.columns(len(row))
        for i, keyword in enumerate(row):
            if cols[i].button(keyword, key=f"related_{row_idx}_{i}_{keyword}", width="stretch"):
                # 클릭 시 검색어로 예약하고 화면 갱신
                st.session_state.pending_keyword = keyword
                st.rerun()
