from typing import List
from google import genai
from config.settings import settings
from domain.news_article import NewsArticle
from utils.exceptions import AppError

def summarize_news(articles: List[NewsArticle]) -> str:
    """
    제공된 뉴스 기사 리스트를 요약하여 한국어 텍스트로 반환합니다.
    
    Args:
        articles (List[NewsArticle]): 요약할 뉴스 기사 리스트
        
    Returns:
        str: AI가 생성한 한국어 요약 텍스트
        
    Raises:
        AppError: API 키 오류, 할당량 초과, 기타 AI 서비스 오류 발생 시
    """
    if not articles:
        return "요약할 기사가 없습니다."

    if not settings.GEMINI_API_KEY:
        raise AppError("api_key_invalid")

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # 뉴스 목록 구성
        news_context = ""
        for i, article in enumerate(articles, 1):
            news_context += f"{i}. 제목: {article.title}\n   내용: {article.snippet}\n\n"
            
        prompt = f"""
다음 뉴스 기사들의 핵심 내용을 한국어로 요약해주세요:
- 불릿 포인트 형식으로 최대 5개 항목
- 각 항목은 1~2문장

[뉴스 목록]
{news_context}
        """
        
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt
        )
        
        if not response.text:
            return "AI 요약 결과를 생성하지 못했습니다."
            
        return response.text.strip()

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
