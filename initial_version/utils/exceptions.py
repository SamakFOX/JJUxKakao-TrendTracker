class AppError(Exception):
    """
    애플리케이션 내에서 발생하는 커스텀 예외 클래스입니다.
    error_type은 utils/error_handler.py의 ERROR_MESSAGES 키와 매칭될 수 있습니다.
    """
    def __init__(self, error_type: str):
        self.error_type = error_type
        super().__init__(error_type)
