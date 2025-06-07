from typing import Protocol, Optional
from fastapi import HTTPException, status, UploadFile, Response
from ..repositories import DataRepositoryFactoryProtocol
from ..schemas.data import DataFileSchema, FileType, HeatmapStatsSchema, HeatmapFirstStatsSchema, HeatmapLongStatsSchema, FileListSchema
from ...tracking.repositories import TrackingRepositoryFactoryProtocol

class DataServiceProtocol(Protocol):
    async def upload_data_file(self, file: UploadFile, test_token: str, stage_id: int) -> DataFileSchema:
        """Загружает файл данных"""
        ...
    
    async def get_files_list(self, test_token: str, file_type: Optional[FileType] = None, stage_id: Optional[int] = None) -> FileListSchema:
        """Получает список файлов с фильтрацией"""
        ...
    
    async def download_file(self, test_token: str, stage_id: int, file_type: FileType) -> Response:
        """Скачивает файл"""
        ...
    
    async def get_heatmap_stats(self, test_token: str, stage_id: int) -> HeatmapStatsSchema:
        """Получает агрегированную статистику по тепловой карте"""
        ...
    
    async def get_heatmap_first_stats(self, test_token: str, stage_id: int) -> HeatmapFirstStatsSchema:
        """Получает статистику по времени до первой фиксации"""
        ...
    
    async def get_heatmap_long_stats(self, test_token: str, stage_id: int) -> HeatmapLongStatsSchema:
        """Получает статистику по длительности фиксаций"""
        ...

class DataServiceImpl:
    def __init__(self, 
                 data_repository: DataRepositoryFactoryProtocol,
                 tracking_repository: TrackingRepositoryFactoryProtocol) -> None:
        self.data_repository = data_repository
        self.tracking_repository = tracking_repository
    
    async def upload_data_file(self, file: UploadFile, test_token: str, stage_id: int) -> DataFileSchema:
        """Загружает файл данных с проверкой существования теста и этапа"""
        
        # Проверяем существование теста
        tracking_repo = await self.tracking_repository.make()
        test = await tracking_repo.get_test_by_token(test_token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        # Проверяем существование этапа
        stage = await tracking_repo.get_stage_by_id(test_token, stage_id)
        if not stage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Этап #{stage_id} в тесте не найден"
            )
        
        # Проверяем тип файла
        if not file.filename or not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть в формате CSV"
            )
        
        # Сохраняем файл
        data_repo = await self.data_repository.make()
        return await data_repo.save_data_file(file, test_token, stage_id, test.name)
    
    async def get_files_list(self, test_token: str, file_type: Optional[FileType] = None, stage_id: Optional[int] = None) -> FileListSchema:
        """Получает список файлов с фильтрацией и проверкой доступа"""
        # Проверяем существование теста
        tracking_repo = await self.tracking_repository.make()
        test = await tracking_repo.get_test_by_token(test_token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        data_repo = await self.data_repository.make()
        return await data_repo.get_files_list(test_token, file_type, stage_id)
    
    async def download_file(self, test_token: str, stage_id: int, file_type: FileType) -> Response:
        """Скачивает файл с проверкой доступа"""
        # Проверяем существование теста
        tracking_repo = await self.tracking_repository.make()
        test = await tracking_repo.get_test_by_token(test_token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        # Получаем содержимое файла
        data_repo = await self.data_repository.make()
        file_content = await data_repo.get_file_content(test_token, stage_id, file_type)
        
        # Определяем MIME тип и расширение
        if file_content.startswith(b'\x89PNG'):  # PNG signature
            media_type = "image/png"
            extension = "png"
        else:
            media_type = "text/csv"
            extension = "csv"
        
        filename = f"{file_type.value}_{stage_id}.{extension}"
        
        return Response(
            content=file_content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    async def get_heatmap_stats(self, test_token: str, stage_id: int) -> HeatmapStatsSchema:
        """Получает агрегированную статистику по тепловой карте"""
        # Проверяем существование теста
        tracking_repo = await self.tracking_repository.make()
        test = await tracking_repo.get_test_by_token(test_token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        data_repo = await self.data_repository.make()
        return await data_repo.get_heatmap_stats(test_token, stage_id)
    
    async def get_heatmap_first_stats(self, test_token: str, stage_id: int) -> HeatmapFirstStatsSchema:
        """Получает статистику по времени до первой фиксации"""
        # Проверяем существование теста
        tracking_repo = await self.tracking_repository.make()
        test = await tracking_repo.get_test_by_token(test_token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        data_repo = await self.data_repository.make()
        return await data_repo.get_heatmap_first_stats(test_token, stage_id)
    
    async def get_heatmap_long_stats(self, test_token: str, stage_id: int) -> HeatmapLongStatsSchema:
        """Получает статистику по длительности фиксаций"""
        # Проверяем существование теста
        tracking_repo = await self.tracking_repository.make()
        test = await tracking_repo.get_test_by_token(test_token)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Тест с указанным токеном не найден"
            )
        
        data_repo = await self.data_repository.make()
        return await data_repo.get_heatmap_long_stats(test_token, stage_id) 