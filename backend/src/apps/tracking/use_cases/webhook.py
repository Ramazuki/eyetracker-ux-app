from src.core.use_cases import UseCaseProtocol
from ..services import TrackingServiceProtocol

WebhookCommandUseCaseProtocol = UseCaseProtocol[dict]

class WebhookCommandUseCaseImpl:
    def __init__(self, service: TrackingServiceProtocol, token: str, stage_id: int, command_type: str, webhook_status: str):
        self.service = service
        self.token = token
        self.stage_id = stage_id
        self.command_type = command_type
        self.webhook_status = webhook_status
    
    async def __call__(self) -> dict:
        return await self.service.receive_webhook_command(
            self.token, 
            self.stage_id,
            self.command_type, 
            self.webhook_status
        ) 