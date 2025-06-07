from typing import Protocol, Dict, Optional, List
import secrets
import json
from src.core.redis_db import get_redis
from ..schemas.tracking import TestSchema, TestCreateSchema, TestStageSchema, StageStatus, CalibrationType

class TrackingRepositoryProtocol(Protocol):
    async def create_test(self, test_data: TestCreateSchema) -> TestSchema:
        """Создает новый тест с уникальным токеном"""
        ...
    
    async def get_test_by_token(self, token: str) -> Optional[TestSchema]:
        """Получает тест по токену"""
        ...
    
    async def get_all_tests(self) -> List[TestSchema]:
        """Получает все тесты"""
        ...
    
    async def create_stage(self, test_token: str, test_number: Optional[int] = None, 
                          calibration_point: Optional[CalibrationType] = None) -> TestStageSchema:
        """Создает новый этап для теста"""
        ...
    
    async def get_stage_by_id(self, test_token: str, stage_id: int) -> Optional[TestStageSchema]:
        """Получает этап по токену теста и номеру этапа"""
        ...
    
    async def update_stage_status(self, test_token: str, stage_id: int, status: StageStatus) -> None:
        """Обновляет статус этапа"""
        ...
    
    async def get_test_stages(self, test_token: str) -> List[TestStageSchema]:
        """Получает все этапы теста"""
        ...
    
    async def get_active_stages(self, test_token: str) -> List[TestStageSchema]:
        """Получает активные (запущенные) этапы теста"""
        ...

class TrackingRepositoryImpl:
    def __init__(self):
        self.redis = get_redis()
    
    def _test_key(self, token: str) -> str:
        """Ключ для теста в Redis"""
        return f"tracking:test:{token}"
    
    def _stage_key(self, test_token: str, stage_id: int) -> str:
        """Ключ для этапа в Redis"""
        return f"tracking:stage:{test_token}:{stage_id}"
    
    def _counter_key(self, test_token: str) -> str:
        """Ключ для счетчика этапов в Redis"""
        return f"tracking:counter:{test_token}"
    
    def _stages_list_key(self, test_token: str) -> str:
        """Ключ для списка этапов теста"""
        return f"tracking:stages:{test_token}"
    
    async def create_test(self, test_data: TestCreateSchema) -> TestSchema:
        """Создает новый тест с уникальным токеном"""
        token = secrets.token_urlsafe(32)
        test = TestSchema(name=test_data.name, token=token)
        
        # Сохраняем тест в Redis
        await self.redis.set(
            self._test_key(token), 
            test.model_dump_json()
        )
        
        # Инициализируем счетчик этапов
        await self.redis.set(self._counter_key(token), 0)
        
        return test
    
    async def get_test_by_token(self, token: str) -> Optional[TestSchema]:
        """Получает тест по токену"""
        test_data = await self.redis.get(self._test_key(token))
        if not test_data:
            return None
        
        return TestSchema.model_validate_json(test_data)
    
    async def get_all_tests(self) -> List[TestSchema]:
        """Получает все тесты"""
        # Получаем все ключи тестов
        pattern = "tracking:test:*"
        keys = await self.redis.keys(pattern)  # type: ignore
        
        tests = []
        for key in keys:
            test_data = await self.redis.get(key)
            if test_data:
                test = TestSchema.model_validate_json(test_data)
                tests.append(test)
        
        # Сортируем по имени
        return sorted(tests, key=lambda x: x.name)
    
    async def create_stage(self, test_token: str, test_number: Optional[int] = None, 
                          calibration_point: Optional[CalibrationType] = None) -> TestStageSchema:
        """Создает новый этап для теста"""
        # Проверяем существование теста
        test = await self.get_test_by_token(test_token)
        if not test:
            raise ValueError(f"Тест с токеном {test_token} не существует")
        
        # Инкрементируем счетчик этапов  
        stage_id = await self.redis.incr(self._counter_key(test_token))  # type: ignore
        
        stage = TestStageSchema(
            test_token=test_token,
            stage_id=stage_id,
            status=StageStatus.CREATED,
            test_number=test_number,
            calibration_point=calibration_point
        )
        
        # Сохраняем этап в Redis
        await self.redis.set(
            self._stage_key(test_token, stage_id), 
            stage.model_dump_json()
        )
        
        # Добавляем ID этапа в список этапов теста
        await self.redis.sadd(self._stages_list_key(test_token), stage_id)  # type: ignore
        
        return stage
    
    async def get_stage_by_id(self, test_token: str, stage_id: int) -> Optional[TestStageSchema]:
        """Получает этап по токену теста и номеру этапа"""
        stage_data = await self.redis.get(self._stage_key(test_token, stage_id))
        if not stage_data:
            return None
        
        return TestStageSchema.model_validate_json(stage_data)
    
    async def update_stage_status(self, test_token: str, stage_id: int, status: StageStatus) -> None:
        """Обновляет статус этапа"""
        stage = await self.get_stage_by_id(test_token, stage_id)
        if stage:
            stage.status = status
            await self.redis.set(
                self._stage_key(test_token, stage_id), 
                stage.model_dump_json()
            )
    
    async def get_test_stages(self, test_token: str) -> List[TestStageSchema]:
        """Получает все этапы теста"""
        # Получаем список ID этапов
        stage_ids = await self.redis.smembers(self._stages_list_key(test_token))  # type: ignore
        if not stage_ids:
            return []
        
        stages = []
        for stage_id_bytes in stage_ids:
            stage_id = int(stage_id_bytes.decode())
            stage = await self.get_stage_by_id(test_token, stage_id)
            if stage:
                stages.append(stage)
        
        # Сортируем по ID этапа
        return sorted(stages, key=lambda x: x.stage_id)
    
    async def get_active_stages(self, test_token: str) -> List[TestStageSchema]:
        """Получает активные (запущенные) этапы теста"""
        all_stages = await self.get_test_stages(test_token)
        return [stage for stage in all_stages if stage.status == StageStatus.STARTED]

class TrackingRepositoryFactoryProtocol(Protocol):
    async def make(self) -> TrackingRepositoryProtocol:
        ...

class TrackingRepositoryFactoryImpl:
    async def make(self) -> TrackingRepositoryProtocol:
        return TrackingRepositoryImpl() 