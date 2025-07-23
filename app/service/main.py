import grpc
from grpc_reflection.v1alpha import reflection
import time

from concurrent import futures

from app.service.photo.mock_repository import MockRepository
from app.service.photo.service import PhotoService
from pb import uploadphoto_pb2, uploadphoto_pb2_grpc


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    repository = MockRepository()
    service = PhotoService(repository)

    uploadphoto_pb2_grpc.add_PhotoServiceServicer_to_server(service, server)

    SERVICE_NAMES = (
        uploadphoto_pb2.DESCRIPTOR.services_by_name[
            "PhotoService"
        ].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port("[::]:50051")
    server.start()

    print("Server started")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
        print("Server stopped")


if __name__ == "__main__":
    serve()