from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import pandas as pd
from .news_article import NewsArticle

@dataclass
class SearchResult:
    """
    한 번의 검색 수행 결과와 AI 요약을 포함하는 데이터 클래스입니다.
    
    Attributes:
        search_key (str): 검색 결과의 고유 키 (예: "키워드-YYYYMMDDHHMM")
        search_time (datetime): 검색이 실행된 실제 시간
        keyword (str): 사용자가 입력한 검색어
        articles (List[NewsArticle]): 검색된 뉴스 기사 객체들의 리스트
        ai_summary (str): AI가 생성한 핵심 요약 텍스트
    """
    search_key: str              # PK, "키워드-yyyymmddhhmm" 형식
    search_time: datetime        # 검색 실행 시간
    keyword: str                 # 검색 키워드
    articles: List[NewsArticle]  # 뉴스 기사 리스트
    ai_summary: str              # AI 요약 결과
    related_keywords: List[str] = field(default_factory=list) # Phase 9: 연관 키워드

    def to_dataframe(self) -> pd.DataFrame:
        """
        검색 결과를 CSV 저장을 위해 Long format(기사 1건=1행)으로 변환합니다.
        9개 컬럼: search_key, search_time, keyword, article_index, title, url, snippet, ai_summary, related_keywords
        """
        data = []
        rel_keywords_str = "|".join(self.related_keywords)
        
        for i, article in enumerate(self.articles, 1):
            data.append({
                "search_key": self.search_key,
                "search_time": self.search_time.strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": self.keyword,
                "article_index": i,
                "title": article.title,
                "url": article.url,
                "snippet": article.snippet,
                "ai_summary": self.ai_summary,
                "related_keywords": rel_keywords_str
            })
        
        # 기사가 없는 경우에도 레코드는 남기기 위해 기본 정보만 추가
        if not data:
            data.append({
                "search_key": self.search_key,
                "search_time": self.search_time.strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": self.keyword,
                "article_index": 0,
                "title": "",
                "url": "",
                "snippet": "",
                "ai_summary": self.ai_summary,
                "related_keywords": rel_keywords_str
            })
            
        return pd.DataFrame(data)
