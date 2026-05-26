import pandas as pd
from requests import Response

from scraper.response.response_handler import ResponseHandler


class EnsogResponseHandler(ResponseHandler):

    def __init__(self) -> None:
        super().__init__()

    def handle(self, response: Response) -> pd.DataFrame:
        df = pd.DataFrame(response.json()["urgentMarketMessages"])

        df["unavailableCapacity"] = pd.to_numeric(df["unavailableCapacity"], errors="coerce")

        df = df[
            (df["eventStatus"] == "Active") &
            (df["isArchived"] != "Yes") &
            (df["unavailableCapacity"].notna()) &
            (df["unavailableCapacity"] > 0)
        ]

        df = df.reset_index(drop=True)
        df["CreatedDate"] = pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M:%S")
        return df
