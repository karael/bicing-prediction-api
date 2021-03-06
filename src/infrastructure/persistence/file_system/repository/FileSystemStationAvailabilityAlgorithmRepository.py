"""
Repository for Station Availability Algorithm with a file system driver
"""
import pickle
import uuid
from typing import Optional
import pandas
from flask_injector import inject

from domain.model.station_availability_algorithm.StationAvailabilityAlgorithm import StationAvailabilityAlgorithm
from domain.model.station_availability_algorithm.StationAvailabilityAlgorithmRepositoryInterface import \
    StationAvailabilityAlgorithmRepositoryInterface
from infrastructure.persistence.file_system import StorageManager


class FileSystemStationAvailabilityAlgorithmRepository(StationAvailabilityAlgorithmRepositoryInterface):
    MODEL_FILE_EXTENSION = 'dat'
    DATA_FRAME_FILE_EXTENSION = 'pkl'

    @inject
    def __init__(self, serializer: pickle, mode_storage_path: str, storage_manager: StorageManager):
        self._serializer = serializer
        self._model_storage_path = mode_storage_path
        self._storage_manager = storage_manager

    def save(self, station_availability_algorithm: StationAvailabilityAlgorithm) -> None:
        station_id = station_availability_algorithm.station_id()
        self._storage_manager.create_storage_location(self._model_storage_path)

        with open(self._model_filename(station_id), "wb") as file:
            self._serializer.dump(station_availability_algorithm.model(), file)

        station_availability_algorithm.training_data_set().to_pickle(
            self._data_training_set_filename(station_id))


    def find_by_station_id(self, station_id: uuid) -> Optional[StationAvailabilityAlgorithm]:
        try:
            with open(self._model_filename(station_id), "rb") as file:
                model = self._serializer.load(file)

            data_frame_train = pandas.read_pickle(self._data_training_set_filename(station_id))

            return StationAvailabilityAlgorithm(station_id, data_frame_train, model)
        except FileNotFoundError:
            return None


    def _model_filename(self, station_id: uuid) -> str:
        return "%s/%s.%s" % (self._model_storage_path, station_id, self.MODEL_FILE_EXTENSION)


    def _data_training_set_filename(self, station_id: uuid) -> str:
        return "%s/%s.%s" % (self._model_storage_path, station_id, self.DATA_FRAME_FILE_EXTENSION)
