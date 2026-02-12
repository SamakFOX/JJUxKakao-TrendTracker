import streamlit as st
from datetime import datetime
from config.settings import settings
from repositories.search_repository import SearchRepository
from services.search_service import search_news
from services.ai_service import summarize_news
from utils.exceptions import AppError
from utils.error_handler import handle_error
from utils.key_generator import generate_search_key
from domain.search_result import SearchResult

from components.search_form import render_search_form
from components.sidebar import (
    render_sidebar_header, render_settings, render_info, 
    render_history_list, render_download_button
)
from components.result_section import render_summary, render_news_list
from components.loading import show_loading

def main():
    """
    TrendTracker 메인 애플리케이션 함수입니다.
    Streamlit UI 구성 및 서비스 레이어와의 통합을 담당합니다.
    """
    # 페이지 설정
    st.set_page_config(page_title="TrendTracker", layout="wide", page_icon="🚀")

    # 리포지토리 초기화
    repository = SearchRepository(settings.CSV_PATH)
    
    # 세션 상태 초기화
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "new_search"
    if "selected_key" not in st.session_state:
        st.session_state.selected_key = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

    # --- 사이드바 영역 ---
    render_sidebar_header()
    num_results = render_settings()
    render_info()
    
    search_keys = repository.get_all_keys()
    keywords_map = {key: key.rsplit('-', 1)[0] for key in search_keys}
    
    selected_history_key = render_history_list(search_keys, keywords_map)
    
    # 히스토리 선택 시 모드 전환
    if selected_history_key and selected_history_key != st.session_state.selected_key:
        st.session_state.current_mode = "history"
        st.session_state.selected_key = selected_history_key
        st.rerun()

    csv_data = repository.get_all_as_csv()
    render_download_button(csv_data, len(search_keys) == 0)

    # --- 메인 영역 ---
    
    # 1. 새 검색 모드
    if st.session_state.current_mode == "new_search":
        st.title("🔍 새로운 트렌드 검색")
        st.markdown("**관심 있는 키워드를 입력하여 최신 뉴스와 AI 분석 결과를 확인하세요.**")
        
        keyword = render_search_form()
        
        if keyword:
            try:
                # 뉴스 검색
                with show_loading("🔍 뉴스를 검색하고 있습니다..."):
                    articles = search_news(keyword, num_results)
                
                if not articles:
                    st.info("검색 결과가 없습니다. 다른 키워드로 시도해보세요.")
                else:
                    # AI 요약
                    with show_loading("🤖 AI가 핵심 내용을 요약하고 있습니다..."):
                        ai_summary = summarize_news(articles)
                    
                    # 결과 객체 생성
                    search_key = generate_search_key(keyword)
                    search_time = datetime.now()
                    
                    result = SearchResult(
                        search_key=search_key,
                        search_time=search_time,
                        keyword=keyword,
                        articles=articles,
                        ai_summary=ai_summary
                    )
                    
                    # 데이터 저장
                    with show_loading("💾 결과를 저장하고 있습니다..."):
                        if repository.save(result):
                            st.session_state.last_result = result
                            st.success(f"'{keyword}' 검색 완료! {len(articles)}건의 뉴스를 찾아서 저장했습니다.")
                            st.rerun()
                        else:
                            handle_error("file_error")
                        
            except AppError as e:
                handle_error(e.error_type)
            except Exception as e:
                st.error(f"애플리케이션 오류가 발생했습니다: {e}")

        # 검색 결과 표시 (방금 검색했거나 세션에 기록이 있는 경우)
        if st.session_state.last_result:
            res = st.session_state.last_result
            render_summary(f"'{res.keyword}' 최신 트렌드 요약", res.ai_summary)
            render_news_list(res.articles)
        else:
            if not search_keys:
                st.info("💡 아직 검색 결과가 없습니다. 위 입력창에 검색어를 입력하여 분석을 시작해보세요!")
            else:
                st.info("💡 새로운 검색어를 입력하거나 왼쪽의 '검색 기록'에서 과거 데이터를 선택하세요.")
            
    # 2. 기록 조회 모드
    elif st.session_state.current_mode == "history" and st.session_state.selected_key:
        st.title("📜 과거 검색 기록")
        
        col1, col2 = st.columns([8, 2])
        with col2:
            if st.button("➕ 새 검색", use_container_width=True):
                st.session_state.current_mode = "new_search"
                st.session_state.selected_key = None
                st.rerun()
        
        with show_loading("기록을 불러오고 있습니다..."):
            result = repository.find_by_key(st.session_state.selected_key)
            
        if result:
            render_summary(f"검색 기록: {result.keyword} ({result.search_time.strftime('%Y-%m-%d %H:%M')})", result.ai_summary)
            render_news_list(result.articles)
        else:
            st.error("해당 기록을 찾을 수 없거나 불러오는 중 오류가 발생했습니다.")
            if st.button("목록으로 돌아가기"):
                st.session_state.current_mode = "new_search"
                st.rerun()

if __name__ == "__main__":
    main()
