from dataclasses import dataclass
from datetime import date
from typing import List, Optional

@dataclass
class SearchFilters:
    """
    고급 검색 필터 정보를 담는 데이터 클래스입니다.
    """
    main_terms: List[str]        # OR 기본 검색어 리스트
    and_terms: List[str]         # 반드시 포함해야 할 단어 리스트
    not_terms: List[str]         # 제외할 단어 리스트
    date_filter_mode: str        # "24h" | "7d" | "30d" | "custom"
    custom_start: Optional[date] # 직접 선택 시작일
    custom_end: Optional[date]   # 직접 선택 종료일
    include_domains: List[str]   # 포함할 도메인 리스트
