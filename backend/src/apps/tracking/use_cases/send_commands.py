from typing import Protocol
from src.core.use_cases import UseCaseProtocol
from ..services import TrackingServiceProtocol
from ..schemas.tracking import StartCommandSchema, StopCommandSchema, TestStageSchema

# Use case для команды старт
SendStartCommandUseCaseProtocol = UseCaseProtocol[TestStageSchema]

class SendStartCommandUseCaseImpl:
    def __init__(self, service: TrackingServiceProtocol, command: StartCommandSchema):
        self.service = service
        self.command = command
    
    async def __call__(self) -> TestStageSchema:
        return await self.service.send_start_command(self.command)

# Use case для команды стоп
SendStopCommandUseCaseProtocol = UseCaseProtocol[dict]

class SendStopCommandUseCaseImpl:
    def __init__(self, service: TrackingServiceProtocol, command: StopCommandSchema):
        self.service = service
        self.command = command
    
    async def __call__(self) -> dict:
        return await self.service.send_stop_command(self.command) 