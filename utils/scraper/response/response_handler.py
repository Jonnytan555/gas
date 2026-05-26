from abc import ABC, abstractmethod
import pandas as pd


class ResponseHandler(ABC):

    def __init__(self, data_path: str = '') -> None:
        self.data_path = data_path

    @abstractmethod
    def handle(self, response) -> pd.DataFrame:
        pass
