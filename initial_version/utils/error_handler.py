import streamlit as st

ERROR_MESSAGES = {
    "api_key_invalid": "API 키를 확인해주세요",
    "tavily_api_key_invalid": "Tavily API 키가 유효하지 않습니다",
    "tavily_limit_exceeded": "월간/분당 검색 한도를 초과했습니다",
    "tavily_server_error": "검색 서버 오류, 잠시 후 재시도해주세요",
    "gemini_rate_limit": "분당 15회 제한 초과, 30초 후 재시도",
    "gemini_bad_request": "요청 형식 오류가 발생했습니다",
    "daily_limit_exceeded": "일일 검색 한도(100건)를 초과했습니다",
    "rate_limit_exceeded": "잠시 후 다시 시도해주세요 (분당 15회 제한)",
    "no_results": "검색 결과가 없습니다",
    "network_error": "네트워크 연결 또는 타임아웃이 발생했습니다",
    "file_error": "파일 접근에 실패했습니다",
    "empty_input": "검색어를 입력해주세요",
    "ai_error": "AI 요약 중 오류가 발생했습니다"
}

def handle_error(error_type: str, level: str = "error"):
    """
    에러 타입에 따라 Streamlit 메시지를 출력합니다.
    - level: 'error', 'warning', 'info'
    """
    message = ERROR_MESSAGES.get(error_type, "알 수 없는 에러가 발생했습니다")
    
    if level == "error":
        st.error(message)
    elif level == "warning":
        st.warning(message)
    elif level == "info":
        st.info(message)
    else:
        st.write(message)
