from typing import List, Dict
from services.search_service import search_news
from domain.search_filters import SearchFilters
from repositories.search_repository import SearchRepository
from config.settings import settings

def get_home_trending_news(repository: SearchRepository, limit: int = 8) -> List[Dict]:
    """
    홈 화면에 표시할 트렌딩 뉴스를 가져옵니다.
    최근 인기 검색어가 있으면 해당 검색어로, 없으면 일반 검색을 수행합니다.
    """
    trending_keywords = repository.get_trending_keywords(hours=24, limit=1)
    
    # 검색어 결정
    search_term = trending_keywords[0] if trending_keywords else "최신 뉴스"
    
    filters = SearchFilters(
        main_terms=[search_term],
        and_terms=[],
        not_terms=[],
        date_filter_mode="24h",
        custom_start=None,
        custom_end=None,
        include_domains=[] # 전체 도메인
    )
    
    try:
        articles = search_news(filters, num_results=limit)
        
        # UI 카드 형식에 맞게 변환
        news_data = []
        for article in articles:
            news_data.append({
                "title": article.title,
                "url": article.url,
                "snippet": article.snippet,
                "pub_date": article.pub_date,
                "source": article.url.split("/")[2] if "//" in article.url else ""
            })
        return news_data
    except Exception as e:
        print(f"[경고] 홈 트렌딩 뉴스 로드 실패: {e}")
        return []
