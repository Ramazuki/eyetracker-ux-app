from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class CalibrationType(int, Enum):
    POINT_1 = 1
    POINT_2 = 2  
    POINT_3 = 3
    POINT_4 = 4

class CommandType(str, Enum):
    START = "start"
    STOP = "stop"

class StageStatus(str, Enum):
    CREATED = "created"
    STARTED = "started" 
    STOPPED = "stopped"

class TestSchema(BaseModel):
    name: str
    token: str

class TestListItemSchema(BaseModel):
    """Схема для элемента списка тестов"""
    name: str
    token: str
    stages_count: int = 0
    created_at: Optional[str] = None

class TestListSchema(BaseModel):
    """Схема для списка всех тестов"""
    tests: List[TestListItemSchema]
    total_count: int

class TestDetailSchema(BaseModel):
    """Детальная информация о тесте"""
    name: str
    token: str
    stages: List['TestStageSchema'] = []
    stages_count: int = 0
    created_at: Optional[str] = None

class TestStageSchema(BaseModel):
    test_token: str
    stage_id: int
    status: StageStatus
    test_number: Optional[int] = None
    calibration_point: Optional[CalibrationType] = None

class StartCommandSchema(BaseModel):
    token: str
    test_number: Optional[int] = None
    calibration_point: Optional[CalibrationType] = None

class StopCommandSchema(BaseModel):
    token: str
    stage_id: int  # Номер этапа для остановки

class WebhookCommandSchema(BaseModel):
    token: str
    stage_id: int  # Номер этапа
    command_type: CommandType
    test_number: Optional[int] = None
    calibration_point: Optional[CalibrationType] = None
    status: str

class TestCreateSchema(BaseModel):
    name: str