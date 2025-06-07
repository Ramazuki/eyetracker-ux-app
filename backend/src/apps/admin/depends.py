from typing import Annotated
from fastapi import Depends

from .repositories import AdminRepositoryFactoryImpl, AdminRepositoryFactoryProtocol, AdminRepositoryProtocol, AdminRepositoryImpl
from .services import AdminServiceImpl, AdminServiceProtocol
from .use_cases import LoginAdminUseCaseImpl, LoginAdminUseCaseProtocol, RegisterAdminUseCaseImpl, RegisterAdminUseCaseProtocol
from .schemas import AdminSchema

# ==== repositories ====
def get_admin_repository() -> AdminRepositoryFactoryProtocol:
    return AdminRepositoryFactoryImpl()

AdminRepositoryFactory = Annotated[AdminRepositoryFactoryProtocol, Depends(get_admin_repository)]

# ==== services ====
def get_admin_service(repository: AdminRepositoryFactory) -> AdminServiceProtocol:
    return AdminServiceImpl(repository)

AdminService = Annotated[AdminServiceProtocol, Depends(get_admin_service)]

# ==== use cases ====
def get_login_admin_use_case(service: AdminService, login: str, password: str) -> LoginAdminUseCaseProtocol:
    return LoginAdminUseCaseImpl(service, login, password)

LoginAdminUseCase = Annotated[LoginAdminUseCaseProtocol, Depends(get_login_admin_use_case)]

def get_register_admin_use_case(service: AdminService, admin: AdminSchema) -> RegisterAdminUseCaseProtocol:
    return RegisterAdminUseCaseImpl(service, admin)

RegisterAdminUseCase = Annotated[RegisterAdminUseCaseProtocol, Depends(get_register_admin_use_case)]