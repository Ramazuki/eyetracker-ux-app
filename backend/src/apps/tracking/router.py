from fastapi import APIRouter
from .depends import CreateTestUseCase, SendStartCommandUseCase, SendStopCommandUseCase, WebhookCommandUseCase, GetCommandsUseCase, GetAllTestsUseCase, GetTestDetailUseCase
from .schemas.tracking import TestSchema, TestStageSchema, TestListSchema, TestDetailSchema
from src.apps.admin.middlewares import AdminToken

router = APIRouter(prefix='/tracking', tags=['Айтрекинг'])

# API эндпоинты для отправки команд
@router.post('/test/create', response_model=TestSchema)
async def create_test(use_case: CreateTestUseCase) -> TestSchema:
    """Создание нового теста с уникальным токеном"""
    return await use_case()

@router.post('/command/start', response_model=TestStageSchema)
async def send_start_command(use_case: SendStartCommandUseCase) -> TestStageSchema:
    """Отправка команды старт - создает и запускает новый этап теста"""
    return await use_case()

@router.post('/command/stop', response_model=dict)
async def send_stop_command(use_case: SendStopCommandUseCase) -> dict:
    """Отправка команды стоп - завершает указанный этап теста"""
    return await use_case()

# Вебхуки для получения подтверждений от приложения
@router.post('/webhook/command', response_model=dict)
async def receive_webhook_command(use_case: WebhookCommandUseCase) -> dict:
    """Вебхук для получения подтверждения команды от приложения айтрекинга"""
    return await use_case()

# Получение команд для клиента
@router.get('/test/{token}/commands', response_model=list)
async def get_commands(use_case: GetCommandsUseCase) -> list:
    """Получение активных команд для токена теста"""
    return await use_case()

# Защищенные endpoints для администратора
@router.get('/admin/tests', response_model=TestListSchema)
async def get_all_tests(admin_token: AdminToken, use_case: GetAllTestsUseCase) -> TestListSchema:
    """Получение списка всех тестов (только для администраторов)"""
    return await use_case()

@router.get('/admin/test/{token}', response_model=TestDetailSchema)
async def get_test_detail(token: str, admin_token: AdminToken, use_case: GetTestDetailUseCase) -> TestDetailSchema:
    """Получение детальной информации о тесте (только для администраторов)"""
    return await use_case(token)
