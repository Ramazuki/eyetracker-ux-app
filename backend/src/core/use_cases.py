from typing import TypeVar, Protocol


UseCaseResultSchemaType = TypeVar('UseCaseResultSchemaType', covariant=True)

class UseCaseProtocol(Protocol[UseCaseResultSchemaType]):
    async def __call__(self) -> UseCaseResultSchemaType:
        ...