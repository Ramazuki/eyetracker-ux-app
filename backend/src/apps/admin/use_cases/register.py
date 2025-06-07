from src.core.use_cases import UseCaseProtocol
from ..services import AdminServiceProtocol
from ..schemas import AdminSchema

RegisterAdminUseCaseProtocol = UseCaseProtocol[str]


class RegisterAdminUseCaseImpl:
    def __init__(self, service: AdminServiceProtocol, admin: AdminSchema) -> None:
        self.service = service
        self.admin = admin
    
    async def __call__(self,) -> str:
        return await self.service.register_admin(self.admin)
