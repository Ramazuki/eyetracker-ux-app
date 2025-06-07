from typing import Protocol, List
import jwt
from datetime import datetime, timedelta, timezone

from src.core.exceptions import UnauthorizedError
from ..repositories import AdminRepositoryFactoryProtocol
from ..schemas import AdminSchema
from ..tools import hash_password, verify_password
from src.settings import settings

class AdminServiceProtocol(Protocol):
    async def register_admin(self, admin: AdminSchema) -> str:
        ...

    async def get_admin(self) -> List[str]:
        ...

    async def login_admin(self, login: str, password: str) -> str:
        ...


class AdminServiceImpl:
    def __init__(self, repository: AdminRepositoryFactoryProtocol) -> None:
        self.repository = repository
    
    def _generate_jwt(self, login: str) -> str:
        """Генерирует JWT токен для админа"""
        now = datetime.now(timezone.utc)
        payload = {
            "login": login,
            "exp": now + timedelta(hours=settings.jwt_expire_hours),
            "iat": now
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    async def register_admin(self, admin: AdminSchema) -> str:
        repo = await self.repository.make()
        
        # Хэшируем пароль перед сохранением
        hashed_password = hash_password(admin.password)
        admin_with_hashed_password = AdminSchema(
            login=admin.login,
            password=hashed_password
        )
        
        await repo.set_admin(admin_with_hashed_password)
        
        # Возвращаем JWT токен
        return self._generate_jwt(admin.login)

    async def login_admin(self, login: str, password: str) -> str:
        repo = await self.repository.make()
        
        # Получаем админа по логину
        stored_admin = await repo.check_admin(login)

        if not verify_password(password, stored_admin.password):
            raise UnauthorizedError(f'Invalid password for admin {login}')
        
        # Возвращаем JWT токен
        return self._generate_jwt(login)

    async def get_admin(self) -> List[str]:
        repo = await self.repository.make()
        return await repo.get_admin()
