from typing import (
    Protocol,
    Iterator,
)

from app.service.photo.mock_repository import PhotoResponseModel


class Repository(Protocol):
    def add_photo(self, photo: PhotoResponseModel) -> PhotoResponseModel: ...

    def get_photo(self, id_: str) -> PhotoResponseModel | None: ...

    def get_random_photos(self, count: int) -> Iterator[PhotoResponseModel]: ...

    def upload_photo(self, chunks: Iterator[bytes]) -> PhotoResponseModel: ...