from typing import Protocol, List

from src.core.exceptions import BadRequestError, UnauthorizedError
from src.core.redis_db import get_redis
from ..tools import hash_password, verify_password

from ..schemas import AdminSchema

class AdminRepositoryProtocol(Protocol):
    async def set_admin(self, admin: AdminSchema) -> None:
        ...

    async def get_admin(self) -> List[str]:
        ...

    async def check_admin(self, login: str) -> AdminSchema:
        ...
    
class AdminRepositoryFactoryProtocol(Protocol):
    async def make(self) -> AdminRepositoryProtocol:
        ...

class AdminRepositoryImpl:
    def __init__(self) -> None:
        self.redis = get_redis()
    
    async def set_admin(self, admin: AdminSchema) -> None:
        if await self.redis.get(admin.login):
            raise BadRequestError(f'Admin with login {admin.login} already exists')
        await self.redis.set(admin.login, admin.password)

    async def get_admin(self) -> List[str]:
        return [login.decode('utf-8') for login in await self.redis.keys('*')]

    async def check_admin(self, login: str) -> AdminSchema:
        hashed_password = await self.redis.get(login)
        if not hashed_password:
            raise UnauthorizedError(f'Admin with login {login} not found')
        return AdminSchema(login=login, password=hashed_password)

class AdminRepositoryFactoryImpl:
    async def make(self) -> AdminRepositoryProtocol:
        return AdminRepositoryImpl()
