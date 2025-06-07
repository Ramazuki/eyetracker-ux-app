from typing import Annotated
from fastapi import Depends

from .repositories import DataRepositoryFactoryImpl, DataRepositoryFactoryProtocol
from .services import DataServiceImpl, DataServiceProtocol
from ..tracking.repositories import TrackingRepositoryFactoryImpl, TrackingRepositoryFactoryProtocol

# ==== repositories ====
def get_data_repository() -> DataRepositoryFactoryProtocol:
    return DataRepositoryFactoryImpl()

DataRepositoryFactory = Annotated[DataRepositoryFactoryProtocol, Depends(get_data_repository)]

def get_tracking_repository() -> TrackingRepositoryFactoryProtocol:
    return TrackingRepositoryFactoryImpl()

TrackingRepositoryFactory = Annotated[TrackingRepositoryFactoryProtocol, Depends(get_tracking_repository)]

# ==== services ====
def get_data_service(
    data_repository: DataRepositoryFactory,
    tracking_repository: TrackingRepositoryFactory
) -> DataServiceProtocol:
    return DataServiceImpl(data_repository, tracking_repository)

DataService = Annotated[DataServiceProtocol, Depends(get_data_service)] 