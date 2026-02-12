from typing import Optional
import streamlit as st
from utils.input_handler import preprocess_keyword

def render_search_form() -> Optional[str]:
    """
    검색어 입력 필드와 검색 버튼을 렌더링합니다.
    유효한 검색어가 입력된 경우 전처리된 키워드를 반환합니다.
    """
    with st.container():
        keyword_input = st.text_input(
            "검색어 입력",
            placeholder="예: 생성형 AI 트렌드, 삼성전자 뉴스 등",
            help="검색하고 싶은 키워드를 입력하세요. (최대 100자)"
        )
        
        search_button = st.button("🔍 뉴스 검색", use_container_width=True)
        
        if search_button:
            if not keyword_input:
                st.warning("검색어를 입력해주세요.")
                return None
            
            processed_keyword = preprocess_keyword(keyword_input)
            if not processed_keyword:
                st.warning("유효한 검색어를 입력해주세요.")
                return None
                
            return processed_keyword
            
    return None
