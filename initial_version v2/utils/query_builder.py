from datetime import date, datetime
from typing import List, Optional
from domain.search_filters import SearchFilters

def parse_terms(raw: str) -> List[str]:
    """
    쉼표(,) 기준 분리 + trim + 빈 값 제거
    """
    if not raw:
        return []
    return [term.strip() for term in raw.split(",") if term.strip()]

def build_query(filters: SearchFilters) -> str:
    """
    OR 기본 쿼리 생성
    예: (고양이 OR 강아지) AND 젤리 NOT 사료
    """
    query_parts = []
    
    # 1. OR 조건 (메인 검색어)
    if filters.main_terms:
        if len(filters.main_terms) > 1:
            or_part = f"({' OR '.join(filters.main_terms)})"
        else:
            or_part = filters.main_terms[0]
        query_parts.append(or_part)
    
    # 2. AND 조건
    for term in filters.and_terms:
        query_parts.append(f"AND {term}")
    
    # 3. NOT 조건
    for term in filters.not_terms:
        query_parts.append(f"NOT {term}")
        
    return " ".join(query_parts)

def resolve_days(
    date_filter_mode: str,
    custom_start: Optional[date],
    custom_end: Optional[date]
) -> Optional[int]:
    """
    Tavily 검색용 최근 N일 값 반환 (days 매개변수용)
    - 24h: 1
    - 7d: 7
    - 30d: 30
    - custom: 현재 날짜와의 차이 계산 (최대값 기준)
    """
    if date_filter_mode == "24h":
        return 1
    elif date_filter_mode == "7d":
        return 7
    elif date_filter_mode == "30d":
        return 30
    elif date_filter_mode == "custom" and custom_start:
        delta = date.today() - custom_start
        return max(1, delta.days)
    
    return None
