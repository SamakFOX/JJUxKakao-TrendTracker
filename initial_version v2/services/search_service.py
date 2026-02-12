from typing import List
from tavily import TavilyClient
from config.settings import settings
from domain.news_article import NewsArticle
from utils.exceptions import AppError
import requests

import requests
import time

def search_news(keyword: str, num_results: int = 5) -> List[NewsArticle]:
    """
    Tavily API를 사용하여 최신 뉴스를 검색하고 NewsArticle 리스트를 반환합니다.
    
    Args:
        keyword (str): 검색할 키워드
        num_results (int): 가져올 기사 개수
        
    Returns:
        List[NewsArticle]: 검색된 기사 리스트
        
    Raises:
        AppError: API 키 오류, 한도 초과, 네트워크 오류 등 발생 시
    """
    if not settings.TAVILY_API_KEY:
        raise AppError("api_key_invalid")

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    
    # 도메인 필터링 설정
    include_domains = [d.strip() for d in settings.SEARCH_DOMAINS.split(",")] if settings.SEARCH_DOMAINS else []
    
    # 충분한 결과를 가져와서 최신순으로 정렬하기 위해 max_results 조정
    max_count = max(num_results * 3, 20)
    
    # 타임아웃 및 재시도 로직
    max_retries = 1
    retry_delay = 1 # 초
    
    for attempt in range(max_retries + 1):
        try:
            # Tavily 클라이언트는 내부적으로 requests를 사용할 수 있으므로 
            # 직접적인 timeout 제어가 어려울 수 있으나, 일반적으로 10초 내외를 기대함.
            response = client.search(
                query=keyword,
                search_depth="advanced",
                include_domains=include_domains,
                max_results=max_count,
                topic="news"
            )
            
            results = response.get('results', [])
            if not results:
                return []
                
            # 최신순 정렬 (published_date 기준 내림차순)
            # 날짜 정보가 없는 항목은 끝으로 보냄
            results.sort(key=lambda x: x.get('published_date', '0000-00-00'), reverse=True)
            
            # 상위 num_results 만큼만 선택
            top_results = results[:num_results]
            
            news_articles = []
            for res in top_results:
                news_articles.append(NewsArticle(
                    title=res.get('title', '제목 없음'),
                    url=res.get('url', ''),
                    snippet=res.get('content', ''), # content를 snippet에 매핑
                    pub_date=res.get('published_date', '') # published_date를 pub_date에 매핑
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
