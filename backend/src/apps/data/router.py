from fastapi import APIRouter, UploadFile, File, Form, Depends, Query, Response
from typing import Optional
from .schemas.data import DataFileSchema, FileType, FileListSchema, HeatmapStatsSchema, HeatmapFirstStatsSchema, HeatmapLongStatsSchema
from .services import DataServiceProtocol
from .depends import get_data_service


router = APIRouter(prefix='/data', tags=['Данные'])

@router.post('/upload', response_model=DataFileSchema)
async def upload_data_file(
    test_token: str = Form(..., description="Токен теста"),
    stage_id: int = Form(..., description="Номер этапа"),
    file: UploadFile = File(..., description="CSV файл с данными"),
    data_service: DataServiceProtocol = Depends(get_data_service)
) -> DataFileSchema:
    """Загрузка файла данных для указанного теста и этапа"""
    return await data_service.upload_data_file(file, test_token, stage_id)

@router.get('/files', response_model=FileListSchema)
async def get_files_list(
    test_token: str = Query(..., description="Токен теста"),
    file_type: Optional[FileType] = Query(None, description="Тип файла (heatmap/saccades)"),
    stage_id: Optional[int] = Query(None, description="Номер этапа"),
    data_service: DataServiceProtocol = Depends(get_data_service)
) -> FileListSchema:
    """Получение списка файлов с фильтрацией"""
    return await data_service.get_files_list(test_token, file_type, stage_id)

@router.get('/download')
async def download_file(
    test_token: str = Query(..., description="Токен теста"),
    stage_id: int = Query(..., description="Номер этапа"),
    file_type: FileType = Query(..., description="Тип файла"),
    data_service: DataServiceProtocol = Depends(get_data_service)
) -> Response:
    """Скачивание файла (CSV или PNG)"""
    return await data_service.download_file(test_token, stage_id, file_type)

@router.get('/stats/heatmap', response_model=HeatmapStatsSchema)
async def get_heatmap_stats(
    test_token: str = Query(..., description="Токен теста"),
    stage_id: int = Query(..., description="Номер этапа"),
    data_service: DataServiceProtocol = Depends(get_data_service)
) -> HeatmapStatsSchema:
    """Получение агрегированной статистики по тепловой карте"""
    return await data_service.get_heatmap_stats(test_token, stage_id)

@router.get('/stats/heatmap-first', response_model=HeatmapFirstStatsSchema)
async def get_heatmap_first_stats(
    test_token: str = Query(..., description="Токен теста"),
    stage_id: int = Query(..., description="Номер этапа"),
    data_service: DataServiceProtocol = Depends(get_data_service)
) -> HeatmapFirstStatsSchema:
    """Получение статистики по времени до первой фиксации"""
    return await data_service.get_heatmap_first_stats(test_token, stage_id)

@router.get('/stats/heatmap-long', response_model=HeatmapLongStatsSchema)
async def get_heatmap_long_stats(
    test_token: str = Query(..., description="Токен теста"),
    stage_id: int = Query(..., description="Номер этапа"),
    data_service: DataServiceProtocol = Depends(get_data_service)
) -> HeatmapLongStatsSchema:
    """Получение статистики по длительности фиксаций"""
    return await data_service.get_heatmap_long_stats(test_token, stage_id) 