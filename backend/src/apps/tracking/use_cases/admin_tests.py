from abc import ABC, abstractmethod
from typing import List
from ..schemas.tracking import TestListSchema, TestDetailSchema, TestListItemSchema, TestStageSchema
from ..services import TrackingServiceProtocol


class GetAllTestsUseCaseProtocol(ABC):
    """Протокол для получения списка всех тестов"""
    
    @abstractmethod
    async def __call__(self) -> TestListSchema:
        pass


class GetTestDetailUseCaseProtocol(ABC):
    """Протокол для получения детальной информации о тесте"""
    
    @abstractmethod
    async def __call__(self, token: str) -> TestDetailSchema:
        pass


class GetAllTestsUseCaseImpl(GetAllTestsUseCaseProtocol):
    """Реализация получения списка всех тестов"""
    
    def __init__(self, tracking_service: TrackingServiceProtocol):
        self._tracking_service = tracking_service
    
    async def __call__(self) -> TestListSchema:
        """Возвращает список всех тестов с базовой информацией"""
        tests_data = await self._tracking_service.get_all_tests()
        
        test_items = []
        for test_data in tests_data:
            # Получаем количество этапов для каждого теста
            stages = await self._tracking_service.get_test_stages(test_data['token'])
            
            test_item = TestListItemSchema(
                name=test_data['name'],
                token=test_data['token'],
                stages_count=len(stages),
                created_at=test_data.get('created_at')
            )
            test_items.append(test_item)
        
        return TestListSchema(
            tests=test_items,
            total_count=len(test_items)
        )


class GetTestDetailUseCaseImpl(GetTestDetailUseCaseProtocol):
    """Реализация получения детальной информации о тесте"""
    
    def __init__(self, tracking_service: TrackingServiceProtocol):
        self._tracking_service = tracking_service
    
    async def __call__(self, token: str) -> TestDetailSchema:
        """Возвращает детальную информацию о тесте включая все этапы"""
        test_data = await self._tracking_service.get_test(token)
        if not test_data:
            raise ValueError(f"Тест с токеном {token} не найден")
        
        stages_data = await self._tracking_service.get_test_stages(token)
        stages = [
            TestStageSchema(
                test_token=stage_data['test_token'],
                stage_id=stage_data['stage_id'],
                status=stage_data['status'],
                test_number=stage_data.get('test_number'),
                calibration_point=stage_data.get('calibration_point')
            )
            for stage_data in stages_data
        ]
        
        return TestDetailSchema(
            name=test_data['name'],
            token=test_data['token'],
            stages=stages,
            stages_count=len(stages),
            created_at=test_data.get('created_at')
        ) 