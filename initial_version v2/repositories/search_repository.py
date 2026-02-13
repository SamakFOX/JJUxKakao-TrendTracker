import os
import pandas as pd
from typing import List, Optional
from datetime import datetime
from domain.search_result import SearchResult
from domain.news_article import NewsArticle

class SearchRepository:
    """
    CSV 파일을 이용하여 검색 기록을 로드, 저장 및 조회하는 리포지토리 클래스입니다.
    
    Attributes:
        csv_path (str): 데이터가 저장될 CSV 파일 경로
        columns (List[str]): CSV 파일의 고유 컬럼 리스트
    """
    def __init__(self, csv_path: str):
        """
        SearchRepository를 초기화합니다. 필요한 경우 데이터 디렉토리를 생성합니다.
        
        Args:
            csv_path (str): 검색 기록을 저장할 파일 경로
        """
        self.csv_path = csv_path
        self.columns = [
            "search_key", "search_time", "keyword", "article_index",
            "title", "url", "snippet", "ai_summary", "related_keywords"
        ]
        # data/ 폴더가 없으면 자동 생성
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

    def load(self) -> pd.DataFrame:
        """
        CSV 파일에서 데이터를 로드합니다. 파일이 없으면 빈 DataFrame을 반환합니다.
        """
        if not os.path.exists(self.csv_path):
            return pd.DataFrame(columns=self.columns)
        
        try:
            df = pd.read_csv(self.csv_path)
            # 컬럼 정합성 확인 (필요시)
            for col in self.columns:
                if col not in df.columns:
                    df[col] = None
            return df[self.columns]
        except Exception as e:
            print(f"[경고] CSV 로드 실패: {e}")
            return pd.DataFrame(columns=self.columns)

    def save(self, search_result: SearchResult) -> bool:
        """
        검색 결과를 CSV 파일에 추가 저장합니다.
        """
        try:
            new_df = search_result.to_dataframe()
            if os.path.exists(self.csv_path):
                existing_df = pd.read_csv(self.csv_path)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
                
            combined_df.to_csv(self.csv_path, index=False, encoding='utf-8-sig')
            return True
        except Exception as e:
            print(f"[에러] CSV 저장 실패: {e}")
            return False

    def get_all_keys(self) -> List[str]:
        """
        저장된 모든 search_key를 검색 시간 기준 최신순으로 정렬하여 반환합니다.
        """
        df = self.load()
        if df.empty:
            return []
        
        # search_key별로 그룹화하여 가장 늦은 search_time을 기준으로 정렬
        # (하나의 search_key에 여러 기사가 있으므로 중복 제거 필요)
        keys_df = df[["search_key", "search_time"]].drop_duplicates()
        keys_df['search_time'] = pd.to_datetime(keys_df['search_time'])
        sorted_keys = keys_df.sort_values(by="search_time", ascending=False)["search_key"].tolist()
        return sorted_keys

    def find_by_key(self, search_key: str) -> Optional[SearchResult]:
        """
        특정 search_key에 해당하는 검색 결과를 SearchResult 객체로 복원하여 반환합니다.
        """
        df = self.load()
        if df.empty:
            return None
        
        target_df = df[df["search_key"] == search_key]
        if target_df.empty:
            return None
            
        # 첫 번째 행에서 기본 정보 추출
        first_row = target_df.iloc[0]
        
        articles = []
        for _, row in target_df.iterrows():
            if row["article_index"] > 0: # 기사가 있는 경우만
                articles.append(NewsArticle(
                    title=str(row["title"]) if pd.notna(row["title"]) else "",
                    url=str(row["url"]) if pd.notna(row["url"]) else "",
                    snippet=str(row["snippet"]) if pd.notna(row["snippet"]) else ""
                ))
        
        try:
            search_time = datetime.strptime(str(first_row["search_time"]), "%Y-%m-%d %H:%M:%S")
        except:
            search_time = datetime.now()
            
        # 연관 키워드 복원
        rel_keywords_raw = str(first_row["related_keywords"]) if pd.notna(first_row.get("related_keywords")) else ""
        related_keywords = [k.strip() for k in rel_keywords_raw.split("|") if k.strip()]

        return SearchResult(
            search_key=str(first_row["search_key"]),
            search_time=search_time,
            keyword=str(first_row["keyword"]),
            articles=articles,
            ai_summary=str(first_row["ai_summary"]) if pd.notna(first_row["ai_summary"]) else "",
            related_keywords=related_keywords
        )

    def get_all_as_csv(self) -> str:
        """
        전체 데이터를 CSV 형식의 문자열로 반환합니다.
        """
        df = self.load()
        if df.empty:
            return ""
        return df.to_csv(index=False, encoding='utf-8-sig')

    def get_trending_keywords(self, hours: int = 24, limit: int = 10) -> List[str]:
        """
        최근 hours 시간 기준 keyword count를 집계하여 상위 리스트를 반환합니다.
        """
        df = self.load()
        if df.empty:
            return []
            
        try:
            # search_time을 datetime으로 변환
            df['search_time'] = pd.to_datetime(df['search_time'])
            
            # 최근 N시간 이내의 데이터 필터링
            now = datetime.now()
            threshold = now - pd.Timedelta(hours=hours)
            recent_df = df[df['search_time'] >= threshold]
            
            if recent_df.empty:
                return []
                
            # 키워드별 중복 제거 (search_key 기준 1회만 카운트하여 키워드 노출 빈도 측정)
            keyword_counts = recent_df[['search_key', 'keyword']].drop_duplicates()['keyword'].value_counts()
            
            return keyword_counts.head(limit).index.tolist()
        except Exception as e:
            print(f"[경고] 인기 검색어 집계 실패: {e}")
            return []
