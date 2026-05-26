from abc import ABC, abstractmethod
import pandas as pd


class PersistenceHandler(ABC):

    @abstractmethod
    def handle(self,
               new_df: pd.DataFrame,
               dropNa: bool = True,
               dtype=None,
               created_date_column: str = 'CreatedDate'):
        pass
