from typing import List, Optional
import streamlit as st
from datetime import datetime

def render_sidebar_header():
    """사이드바 상단 제목과 소개를 렌더링합니다."""
    st.sidebar.title("🚀 TrendTracker")
    st.sidebar.markdown("**키워드로 뉴스를 검색하고 AI가 요약해드립니다.**")
    st.sidebar.markdown("---")

def render_settings() -> int:
    """검색 건수 설정을 위한 슬라이더를 렌더링하고 선택된 값을 반환합니다."""
    st.sidebar.subheader("⚙️ 설정")
    num_results = st.sidebar.slider(
        "검색 결과 개수",
        min_value=1,
        max_value=10,
        value=5,
        help="가져올 뉴스 기사의 최대 개수를 설정합니다."
    )
    return num_results

def render_info():
    """사용법, API 한도, 데이터 저장 안내 섹션을 렌더링합니다."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ 정보")
    
    with st.sidebar.expander("📖 사용법", expanded=False):
        st.markdown("""
        1. **키워드 입력**: 메인 화면에서 검색어를 입력합니다.
        2. **결과 확인**: 최신 뉴스와 AI 핵심 요약을 확인합니다.
        3. **히스토리**: 왼쪽 목록에서 과거 검색 기록을 볼 수 있습니다.
        4. **내보내기**: 하단 버튼으로 전체 기록을 저장하세요.
        """)
        
    with st.sidebar.expander("📊 API 한도", expanded=False):
        st.markdown("""
        - **Tavily**: 무료 플랜 기준 월 1,000건 검색 가능
        - **Gemini**: 무료 티어 기준 분당 요청 횟수 제한 있음
        """)
        
    with st.sidebar.expander("💾 데이터 저장 안내", expanded=True):
        st.info("""
        - 검색 기록은 CSV 파일(`data/search_history.csv`)에 저장됩니다.
        - CSV 파일을 삭제하면 이전 기록이 사라집니다.
        - 중요한 데이터는 주기적인 다운로드를 권장합니다.
        """)

def render_history_list(search_keys: List[str], keywords_map: dict = None) -> Optional[str]:
    """과거 검색 기록 목록을 렌더링하고 선택된 search_key를 반환합니다."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 검색 기록")
    
    if not search_keys:
        st.sidebar.write("저장된 검색 기록이 없습니다.")
        return None
    
    # "키워드 (yyyy-mm-dd HH:MM)" 형식으로 옵션 생성
    options = []
    key_map = {}
    
    for key in search_keys:
        try:
            # keywords_map이 있으면 키워드를 가져오고, 없으면 키에서 추출
            keyword = keywords_map.get(key) if keywords_map else key.rsplit('-', 1)[0]
            ts_str = key.rsplit('-', 1)[1]
            dt = datetime.strptime(ts_str, "%Y%m%d%H%M")
            display_str = f"{keyword} ({dt.strftime('%Y-%m-%d %H:%M')})"
        except:
            display_str = key
            
        options.append(display_str)
        key_map[display_str] = key
        
    selected_option = st.sidebar.selectbox(
        "히스토리 선택",
        options=options,
        index=None,
        placeholder="과거 결과 선택..."
    )
    
    return key_map.get(selected_option) if selected_option else None

def render_download_button(csv_data: str, is_empty: bool):
    """CSV 다운로드 버튼을 렌더링합니다."""
    st.sidebar.markdown("---")
    
    if is_empty:
        st.sidebar.button("📥 CSV 다운로드", disabled=True, help="저장된 데이터가 없습니다.")
    else:
        st.sidebar.download_button(
            label="📥 CSV 다운로드",
            data=csv_data,
            file_name=f"trendtracker_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
