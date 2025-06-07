from fastapi import APIRouter
from .depends import LoginAdminUseCase, RegisterAdminUseCase

router = APIRouter(prefix='/admin', tags=['Администратор'])

@router.post('/register', response_model=str)
async def register_admin(use_case: RegisterAdminUseCase) -> str:
    return await use_case()

@router.post('/login', response_model=str)
async def login_admin(use_case: LoginAdminUseCase) -> str:
    return await use_case()