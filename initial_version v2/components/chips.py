import streamlit as st
from typing import List, Dict

def render_category_chips(categories: Dict[str, List[str]], selected_categories: List[str]) -> List[str]:
    """
    도메인 카테고리를 칩(버튼) 형태로 렌더링하고 선택된 카테고리 리스트를 반환합니다.
    """
    st.write("**도메인 필터 (다중 선택)**")
    
    # 칩들을 가로로 배치하기 위해 컬럼 생성 또는 간격 조정
    # Streamlit은 공식적인 chip 컴포넌트가 없으므로 버튼 스타일링이나 layout 활용
    
    cols = st.columns(len(categories))
    new_selected = list(selected_categories)
    
    for i, (name, domains) in enumerate(categories.items()):
        is_selected = name in new_selected
        
        # 버튼 스타일 (선택 여부에 따라 다르게 표시)
        button_type = "primary" if is_selected else "secondary"
        
        if cols[i].button(name, key=f"chip_{name}", width='stretch', type=button_type):
            if is_selected:
                new_selected.remove(name)
            else:
                new_selected.append(name)
            st.rerun()
            
    return new_selected

def get_selected_domains(categories: Dict[str, List[str]], selected_category_names: List[str]) -> List[str]:
    """
    선택된 카테고리 이름들을 실제 도메인 리스트로 변환합니다.
    """
    domains = []
    for name in selected_category_names:
        if name in categories:
            domains.extend(categories[name])
    return list(set(domains)) # 중복 제거
