import streamlit as st
from contextlib import contextmanager

@contextmanager
def show_loading(message: str = "처리 중입니다..."):
    """
    Streamlit spinner를 사용하여 로딩 상태를 표시하는 컨텍스트 매니저입니다.
    """
    with st.spinner(message):
        yield
