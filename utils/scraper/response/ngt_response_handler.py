import pandas as pd
from datetime import datetime, timezone

from scraper.response.response_handler import ResponseHandler


class NgtResponseHandler(ResponseHandler):
    """
    Parse the National Gas REST API publications/gasday response.

    Response shape:
      [{"publicationId": "PUBOB637",
        "publications": [{"applicableFor": "2024-02-29", "value": "302.5", ...}]
      }, ...]

    applicableFor is the gas day; value is in mcm/d.
    """

    def __init__(self, data_item_map: dict) -> None:
        super().__init__()
        self._id_to_name = {v: k for k, v in data_item_map.items()}

    def handle(self, response) -> pd.DataFrame:
        data = response.json()
        if not data:
            return pd.DataFrame()

        created_at = datetime.now(timezone.utc).isoformat()
        rows = []
        for pub in data:
            pub_id    = pub.get("publicationId", "")
            data_item = self._id_to_name.get(pub_id, pub_id)
            for record in pub.get("publications", []):
                applicable_for = record.get("applicableFor", "")
                value          = record.get("value")
                if applicable_for and value is not None:
                    rows.append({
                        "applicable_at": applicable_for,
                        "data_item":     data_item,
                        "value":         float(value),
                        "unit":          "mcm/d",
                        "created_at":    created_at,
                    })
        return pd.DataFrame(rows)
