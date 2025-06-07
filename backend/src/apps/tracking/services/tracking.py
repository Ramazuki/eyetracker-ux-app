from typing import Protocol, List, Optional
from fastapi import HTTPException, status
from ..repositories import TrackingRepositoryFactoryProtocol
from ..schemas.tracking import TestSchema, TestCreateSchema, StartCommandSchema, StopCommandSchema, TestStageSchema, StageStatus

class TrackingServiceProtocol(Protocol):
    async def create_test(self, test_data: TestCreateSchema) -> TestSchema:
        """Создает новый тест"""
        ...
    
    async def deactivate_test(self, token: str) -> dict:
        """Деактивирует тест"""
        ...
    
    async def send_start_command(self, command: StartCommandSchema) -> TestStageSchema:
        """Отправляет команду старт - создает новый этап"""
        ...
    
    async def send_stop_command(self, command: StopCommandSchema) -> dict:
        """Отправляет команду стоп - завершает указанный этап"""
        ...
    
    async def receive_webhook_command(self, token: str, stage_id: int, command_type: str, webhook_status: str) -> dict:
        """Обрабатывает вебхук команды от приложения"""
        ...
    
    async def get_pending_commands(self, token: str) -> list:
        """Получает команды для токена теста"""
        ...
    
    async def get_all_tests(self) -> List[dict]:
        """Получает список всех тестов"""
        ...
    
    async def get_test(self, token: str) -> Optional[dict]:
        """Получает тест по токену"""
        ...
    
    async def get_test_stages(self, token: str) -> List[dict]:
        """Получает все этапы теста"""
        ...

class TrackingServiceImpl:
    def __init__(self, repository: TrackingRepositoryFactoryProtocol) -> None:
        self.repository = repository
    
    async def create_test(self, test_data: TestCreateSchema) -> TestSchema:
        """Создает новый тест с уникальным токеном"""
        repo = await self.repository.make()
        return await repo.create_test(test_data)
    
    async def deactivate_test(self, token: str) -> dict:
        """Деактивирует тест и останавливает все активные этапы"""
        repo = await self.repository.make()
        
        # Проверяем существование теста
        test = await repo.get_test_by_token(token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        # Получаем и останавливаем все активные этапы
        active_stages = await repo.get_active_stages(token)
        stopped_stages = []
        
        for stage in active_stages:
            await repo.update_stage_status(token, stage.stage_id, StageStatus.STOPPED)
            stopped_stages.append(stage.stage_id)
        
        return {
            "message": f"Тест '{test.name}' деактивирован",
            "test_token": token,
            "test_name": test.name,
            "stopped_stages": stopped_stages,
            "total_stopped": len(stopped_stages)
        }
    
    async def send_start_command(self, command: StartCommandSchema) -> TestStageSchema:
        """Отправляет команду старт - создает и запускает новый этап теста"""
        repo = await self.repository.make()
        
        # Проверяем существование теста
        test = await repo.get_test_by_token(command.token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        # Создаем новый этап
        stage = await repo.create_stage(
            test_token=command.token,
            test_number=command.test_number,
            calibration_point=command.calibration_point
        )
        
        # Сразу запускаем этап
        await repo.update_stage_status(command.token, stage.stage_id, StageStatus.STARTED)
        stage.status = StageStatus.STARTED
        
        return stage
    
    async def send_stop_command(self, command: StopCommandSchema) -> dict:
        """Отправляет команду стоп - завершает указанный этап"""
        repo = await self.repository.make()
        
        # Проверяем существование теста
        test = await repo.get_test_by_token(command.token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        # Проверяем существование этапа
        stage = await repo.get_stage_by_id(command.token, command.stage_id)
        if not stage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Этап #{command.stage_id} в тесте не найден"
            )
        
        # Проверяем, что этап был запущен
        if stage.status != StageStatus.STARTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Можно остановить только запущенный этап"
            )
        
        # Останавливаем этап
        await repo.update_stage_status(command.token, command.stage_id, StageStatus.STOPPED)
        
        return {
            "message": f"Этап #{command.stage_id} успешно остановлен",
            "test_token": command.token,
            "stage_id": command.stage_id,
            "test_name": test.name
        }
    
    async def receive_webhook_command(self, token: str, stage_id: int, command_type: str, webhook_status: str) -> dict:
        """Обрабатывает вебхук подтверждения команды от приложения"""
        repo = await self.repository.make()
        
        # Проверяем существование теста
        test = await repo.get_test_by_token(token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        # Проверяем существование этапа
        stage = await repo.get_stage_by_id(token, stage_id)
        if not stage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Этап #{stage_id} в тесте не найден"
            )
        
        return {
            "message": f"Подтверждение команды {command_type} для этапа #{stage_id} получено",
            "test_token": token,
            "stage_id": stage_id,
            "status": webhook_status,
            "test_name": test.name
        }
    
    async def get_pending_commands(self, token: str) -> list:
        """Получает команды для токена (активные этапы как start, остановленные как stop)"""
        repo = await self.repository.make()
        
        # Проверяем существование теста
        test = await repo.get_test_by_token(token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        # Получаем все этапы
        all_stages = await repo.get_test_stages(token)
        
        # Формируем команды
        commands = []
        for stage in all_stages:
            if stage.status == StageStatus.STARTED:
                commands.append({
                    "command": "start",
                    "stage_id": stage.stage_id,
                    "test_number": stage.test_number,
                    "calibration_point": stage.calibration_point,
                    "status": stage.status.value
                })
            elif stage.status == StageStatus.STOPPED:
                commands.append({
                    "command": "stop",
                    "stage_id": stage.stage_id,
                    "test_number": stage.test_number,
                    "calibration_point": stage.calibration_point,
                    "status": stage.status.value
                })
        
        return commands 
    
    async def get_all_tests(self) -> List[dict]:
        """Получает список всех тестов"""
        repo = await self.repository.make()
        tests = await repo.get_all_tests()
        
        return [
            {
                "name": test.name,
                "token": test.token,
                "created_at": None  # Можно добавить позже
            }
            for test in tests
        ]
    
    async def get_test(self, token: str) -> Optional[dict]:
        """Получает тест по токену"""
        repo = await self.repository.make()
        test = await repo.get_test_by_token(token)
        
        if not test:
            return None
        
        return {
            "name": test.name,
            "token": test.token,
            "created_at": None  # Можно добавить позже
        }
    
    async def get_test_stages(self, token: str) -> List[dict]:
        """Получает все этапы теста"""
        repo = await self.repository.make()
        stages = await repo.get_test_stages(token)
        
        return [
            {
                "test_token": stage.test_token,
                "stage_id": stage.stage_id,
                "status": stage.status.value,
                "test_number": stage.test_number,
                "calibration_point": stage.calibration_point
            }
            for stage in stages
        ] 