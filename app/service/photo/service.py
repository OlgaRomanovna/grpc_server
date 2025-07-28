import grpc

import pb.uploadphoto_pb2_grpc as photo_pb2_grpc
import pb.uploadphoto_pb2 as photo_pb2
import datetime
import uuid
import time
from typing import Iterator

from grpc import ServicerContext, StatusCode
import google.protobuf.timestamp_pb2 as timestamp_pb2

from app.service.photo.mock_repository import (
    PhotoResponseModel,
    TimeStampModel,
)
from app.service.photo.protocol import Repository


class PhotoService(photo_pb2_grpc.PhotoServiceServicer):
    def __init__(self, repository: Repository) -> None:
        self._repository = repository

    def Photo(
        self, request: photo_pb2.IdRequest, context: ServicerContext
    ) -> photo_pb2.PhotoResponse:
        photo = self._repository.get_photo(request.id)
        if not photo:
            context.set_code(StatusCode.NOT_FOUND)
            context.set_details(f"Photo with id {request.id} not found!")
            return photo_pb2.PhotoResponse()

        response = photo_pb2.PhotoResponse(
            id=photo.id,
            description=photo.description,
            timestamp=timestamp_pb2.Timestamp(
                seconds=photo.timestamp.seconds, nanos=photo.timestamp.nanos
            ),
            content=photo.content,
        )

        return response

    def AddPhoto(
        self, request: photo_pb2.PhotoRequest, context: ServicerContext
    ) -> photo_pb2.PhotoResponse:
        id_ = str(uuid.uuid4())
        photo_response = photo_pb2.PhotoResponse(
            id=id_,
            description=request.description,
            content=request.content,
        )
        now = timestamp_pb2.Timestamp()
        now.FromDatetime(datetime.datetime.now())
        photo_response.timestamp.CopyFrom(now)

        photo_model = PhotoResponseModel(
            id=photo_response.id,
            description=photo_response.description,
            timestamp=TimeStampModel(
                seconds=photo_response.timestamp.seconds,
                nanos=photo_response.timestamp.nanos,
            ),
            content=photo_response.content,
        )
        self._repository.add_photo(photo_model)

        return photo_response

    def RandomPhotos(
        self, request: photo_pb2.CountRequest, context: ServicerContext
    ) -> Iterator[photo_pb2.PhotoResponse]:
        for photo in self._repository.get_random_photos(request.count):
            response = photo_pb2.PhotoResponse(
                id=photo.id,
                description=photo.description,
                timestamp=timestamp_pb2.Timestamp(
                    seconds=photo.timestamp.seconds, nanos=photo.timestamp.nanos
                ),
                content=photo.content,
            )
            time.sleep(1)
            yield response

    def UploadPhotos(
            self,
            request_iterator: Iterator[photo_pb2.PhotoRequest],
            context: grpc.ServicerContext,
    ) -> photo_pb2.UploadStatus:
        try:
            for request in request_iterator:
                photo = PhotoResponseModel(
                    id=str(uuid.uuid4()),
                    description=request.description,
                    content=request.content,
                    timestamp=datetime.datetime.Timestamp(),
                )
                self._repository.add_photo(photo)

            return photo_pb2.UploadStatus(
                success=True,
                message="Upload completed successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return photo_pb2.UploadStatus(success=False, message=str(e))
