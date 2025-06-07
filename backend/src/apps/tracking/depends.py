from typing import Annotated
from fastapi import Depends

from .repositories import TrackingRepositoryFactoryImpl, TrackingRepositoryFactoryProtocol
from .services import TrackingServiceImpl, TrackingServiceProtocol
from .use_cases import (
    CreateTestUseCaseImpl, CreateTestUseCaseProtocol,
    SendStartCommandUseCaseImpl, SendStartCommandUseCaseProtocol,
    SendStopCommandUseCaseImpl, SendStopCommandUseCaseProtocol,
    WebhookCommandUseCaseImpl, WebhookCommandUseCaseProtocol,
    GetCommandsUseCaseImpl, GetCommandsUseCaseProtocol,
    GetAllTestsUseCaseImpl, GetAllTestsUseCaseProtocol,
    GetTestDetailUseCaseImpl, GetTestDetailUseCaseProtocol
)
from .schemas.tracking import TestCreateSchema, StartCommandSchema, StopCommandSchema, WebhookCommandSchema

# ==== repositories ====
def get_tracking_repository() -> TrackingRepositoryFactoryProtocol:
    return TrackingRepositoryFactoryImpl()

TrackingRepositoryFactory = Annotated[TrackingRepositoryFactoryProtocol, Depends(get_tracking_repository)]

# ==== services ====
def get_tracking_service(repository: TrackingRepositoryFactory) -> TrackingServiceProtocol:
    return TrackingServiceImpl(repository)

TrackingService = Annotated[TrackingServiceProtocol, Depends(get_tracking_service)]

# ==== use cases ====
def get_create_test_use_case(service: TrackingService, test_data: TestCreateSchema) -> CreateTestUseCaseProtocol:
    return CreateTestUseCaseImpl(service, test_data)

CreateTestUseCase = Annotated[CreateTestUseCaseProtocol, Depends(get_create_test_use_case)]

def get_send_start_command_use_case(service: TrackingService, command: StartCommandSchema) -> SendStartCommandUseCaseProtocol:
    return SendStartCommandUseCaseImpl(service, command)

SendStartCommandUseCase = Annotated[SendStartCommandUseCaseProtocol, Depends(get_send_start_command_use_case)]

def get_send_stop_command_use_case(service: TrackingService, command: StopCommandSchema) -> SendStopCommandUseCaseProtocol:
    return SendStopCommandUseCaseImpl(service, command)

SendStopCommandUseCase = Annotated[SendStopCommandUseCaseProtocol, Depends(get_send_stop_command_use_case)]

def get_webhook_command_use_case(service: TrackingService, token: str, stage_id: int, command_type: str, webhook_status: str) -> WebhookCommandUseCaseProtocol:
    return WebhookCommandUseCaseImpl(service, token, stage_id, command_type, webhook_status)

WebhookCommandUseCase = Annotated[WebhookCommandUseCaseProtocol, Depends(get_webhook_command_use_case)]

def get_commands_use_case(service: TrackingService, token: str) -> GetCommandsUseCaseProtocol:
    return GetCommandsUseCaseImpl(service, token)

GetCommandsUseCase = Annotated[GetCommandsUseCaseProtocol, Depends(get_commands_use_case)]

# ==== Admin use cases ====
def get_all_tests_use_case(service: TrackingService) -> GetAllTestsUseCaseProtocol:
    return GetAllTestsUseCaseImpl(service)

GetAllTestsUseCase = Annotated[GetAllTestsUseCaseProtocol, Depends(get_all_tests_use_case)]

def get_test_detail_use_case(service: TrackingService) -> GetTestDetailUseCaseProtocol:
    return GetTestDetailUseCaseImpl(service)

GetTestDetailUseCase = Annotated[GetTestDetailUseCaseProtocol, Depends(get_test_detail_use_case)]