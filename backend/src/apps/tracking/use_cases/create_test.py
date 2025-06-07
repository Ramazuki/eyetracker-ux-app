from typing import Protocol
from src.core.use_cases import UseCaseProtocol
from ..services import TrackingServiceProtocol
from ..schemas.tracking import TestSchema, TestCreateSchema

CreateTestUseCaseProtocol = UseCaseProtocol[TestSchema]

class CreateTestUseCaseImpl:
    def __init__(self, service: TrackingServiceProtocol, test_data: TestCreateSchema):
        self.service = service
        self.test_data = test_data
    
    async def __call__(self) -> TestSchema:
        return await self.service.create_test(self.test_data) 