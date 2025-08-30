# store/core/exceptions.py

class BaseException(Exception):
    """Exceção base com mensagem e status code."""
    status_code: int = 500
    message: str = "Internal Server Error"

    def __init__(self, message: str | None = None) -> None:
        if message:
            self.message = message
        super().__init__(self.message)


class NotFoundException(BaseException):
    status_code = 404
    message = "Not Found"


class DBInsertException(BaseException):
    status_code = 400
    message = "Erro ao inserir no banco de dados"
