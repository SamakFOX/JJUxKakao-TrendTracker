from dataclasses import dataclass

@dataclass
class NewsArticle:
    """
    뉴스 기사의 정보를 담는 데이터 클래스입니다.
    
    Attributes:
        title (str): 기사의 제목
        url (str): 기사의 원문 URL
        snippet (str): 기사의 요약 내용 또는 스니펫
        pub_date (str): 기사의 발행일 (YYYY-MM-DD 형식 권장)
    """
    title: str       # 기사 제목
    url: str         # 기사 URL
    snippet: str     # 기사 스니펫
    pub_date: str = ""  # 발행일 (YYYY-MM-DD 형식 권장)
