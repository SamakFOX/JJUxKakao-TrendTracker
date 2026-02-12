import os
from dotenv import load_dotenv

class Settings:
    """
    애플리케이션 설정을 관리하는 클래스입니다.
    .env 파일에서 환경 변수를 로드하고 유효성을 검사합니다.
    """
    def __init__(self):
        # .env 파일 로드
        load_dotenv()
        
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.CSV_PATH = os.getenv("CSV_PATH")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.SEARCH_DOMAINS = os.getenv("SEARCH_DOMAINS", "")
        
        # 필수 환경 변수 확인
        self._validate()

    def _validate(self):
        """
        필수 환경 변수가 로드되었는지 확인합니다.
        """
        missing = []
        if not self.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")
        if not self.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not self.CSV_PATH:
            missing.append("CSV_PATH")
            
        if missing:
            error_msg = f"\n❌ 환경변수가 설정되지 않았습니다.\n\n"
            error_msg += f"누락된 변수: {', '.join(missing)}\n\n"
            error_msg += "설정 방법:\n"
            error_msg += "1. 프로젝트 루트에 .env 파일을 생성하세요.\n"
            error_msg += "2. .env.example 내용을 .env로 복사하세요.\n"
            error_msg += "3. 각 API 키를 발급받아 입력하세요.\n\n"
            error_msg += "API 키 발급 안내:\n"
            error_msg += "- Tavily API: https://tavily.com/\n"
            error_msg += "- Google AI Studio (Gemini): https://aistudio.google.com/\n"
            raise ValueError(error_msg)

# 싱글톤 패턴으로 사용할 인스턴스 생성
settings = Settings()
