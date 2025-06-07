from src.core.use_cases import UseCaseProtocol
from ..services import TrackingServiceProtocol

GetCommandsUseCaseProtocol = UseCaseProtocol[list]

class GetCommandsUseCaseImpl:
    def __init__(self, service: TrackingServiceProtocol, token: str):
        self.service = service
        self.token = token
    
    async def __call__(self) -> list:
        return await self.service.get_pending_commands(self.token) 