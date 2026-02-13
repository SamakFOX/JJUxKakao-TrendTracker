from dataclasses import dataclass
from typing import List
from google import genai
from config.settings import settings
from domain.news_article import NewsArticle
from utils.exceptions import AppError

@dataclass
class AiOutput:
    """
    AI 서비스의 통합 출력 구조입니다.
    """
    summary: str
    related_keywords: List[str]

def summarize_news_with_keywords(articles: List[NewsArticle]) -> AiOutput:
    """
    뉴스 기사 리스트를 요약하고 연관 키워드를 제안합니다.
    """
    if not articles:
        return AiOutput(summary="요약할 기사가 없습니다.", related_keywords=[])

    if not settings.GEMINI_API_KEY:
        raise AppError("api_key_invalid")

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # 뉴스 목록 구성
        news_context = ""
        for i, article in enumerate(articles, 1):
            news_context += f"{i}. 제목: {article.title}\n   내용: {article.snippet}\n\n"
            
        prompt = f"""
다음 뉴스 기사들의 핵심 내용을 한국어로 요약하고, 관련 있는 연관 키워드를 추출해주세요:

[요구사항]
1. 요약: 불릿 포인트 형식으로 최대 5개 항목, 각 항목은 1~2문장
2. 연관 키워드: 기사 내용과 밀접하게 관련된 키워드 5~10개를 쉼표(,)로 구분하여 제시

[출력 형식]
요약:
(요약 내용)

연관 키워드:
(키워드1, 키워드2, ...)

[뉴스 목록]
{news_context}
        """
        
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )
        
        text = response.text if response.text else ""
        
        # 결과 파싱
        summary = ""
        related_keywords = []
        
        if "요약:" in text and "연관 키워드:" in text:
            parts = text.split("연관 키워드:")
            summary = parts[0].replace("요약:", "").strip()
            raw_keywords = parts[1].strip()
            related_keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]
        else:
            summary = text.strip()
            
        return AiOutput(summary=summary, related_keywords=related_keywords)

    except Exception as e:
        err_str = str(e).lower()
        if "api key" in err_str or "unauthorized" in err_str:
            raise AppError("api_key_invalid")
        elif "quota" in err_str or "429" in err_str or "limit" in err_str:
            raise AppError("gemini_rate_limit")
        elif "400" in err_str or "invalid" in err_str:
            raise AppError("gemini_bad_request")
        else:
            raise AppError("ai_error")

def summarize_news(articles: List[NewsArticle]) -> str:
    """
    기존 하위 호환성을 위한 요약 함수입니다.
    """
    output = summarize_news_with_keywords(articles)
    return output.summary
