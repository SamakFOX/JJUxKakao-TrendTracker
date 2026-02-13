import requests
import time
from typing import List
from tavily import TavilyClient
from config.settings import settings
from domain.news_article import NewsArticle
from domain.search_filters import SearchFilters
from utils.exceptions import AppError
from utils.query_builder import build_query, resolve_days

def search_news(filters: SearchFilters, num_results: int = 5) -> List[NewsArticle]:
    """
    Tavily API를 사용하여 조건 기반 뉴스를 검색하고 NewsArticle 리스트를 반환합니다.
    """
    if not settings.TAVILY_API_KEY:
        raise AppError("api_key_invalid")

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    
    # 쿼리 생성
    query = build_query(filters)
    if not query:
        return []

    # 검색 기간(days) 설정
    days = resolve_days(filters.date_filter_mode, filters.custom_start, filters.custom_end)
    
    # 도메인 필터링
    include_domains = filters.include_domains if filters.include_domains else []
    
    # 충분한 결과를 가져와서 최신순으로 정렬하기 위해 max_results 조정
    max_count = max(num_results * 5, 20)
    
    # 타임아웃 및 재시도 로직
    max_retries = 1
    retry_delay = 1 # 초
    
    for attempt in range(max_retries + 1):
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                include_domains=include_domains,
                days=days,
                max_results=max_count,
                topic="news"
            )
            
            results = response.get('results', [])
            if not results:
                return []
                
            # 최신순 정렬 (published_date 기준 내림차순)
            results.sort(key=lambda x: x.get('published_date', '0000-00-00'), reverse=True)
            
            # 상위 num_results 만큼만 선택
            top_results = results[:num_results]
            
            news_articles = []
            for res in top_results:
                news_articles.append(NewsArticle(
                    title=res.get('title', '제목 없음'),
                    url=res.get('url', ''),
                    snippet=res.get('content', ''),
                    pub_date=res.get('published_date', '')
                ))
                
            return news_articles

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code == 401:
                raise AppError("tavily_api_key_invalid")
            elif status_code == 429:
                raise AppError("tavily_limit_exceeded")
            elif status_code and 500 <= status_code < 600:
                raise AppError("tavily_server_error")
            elif status_code == 400:
                raise AppError("tavily_api_key_invalid") # 혹은 잘못된 요청
            
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue
            raise AppError("network_error")

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue
            raise AppError("network_error")
            
        except Exception as e:
            err_msg = str(e).lower()
            if "api key" in err_msg:
                raise AppError("tavily_api_key_invalid")
            elif "429" in err_msg:
                raise AppError("tavily_limit_exceeded")
            
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue
            raise AppError("network_error")
            
    return []
