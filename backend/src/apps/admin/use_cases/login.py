from src.core.use_cases import UseCaseProtocol
from ..services import AdminServiceProtocol

LoginAdminUseCaseProtocol = UseCaseProtocol[str]

class LoginAdminUseCaseImpl:
    def __init__(self, service: AdminServiceProtocol, login: str, password: str) -> None:
        self.service = service
        self.login = login
        self.password = password
    
    async def __call__(self,) -> str:
        return await self.service.login_admin(self.login, self.password)