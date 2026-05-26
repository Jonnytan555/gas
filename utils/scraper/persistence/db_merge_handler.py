import logging
import uuid

import pandas as pd
import sqlalchemy as sa

from scraper.persistence.db_upsert_handler import DbUpsertHandler


class DbMergeHandler(DbUpsertHandler):
    """Full MERGE (UPDATE existing + INSERT new). Use when rows may be amended after publication."""

    def __init__(
        self,
        engine: sa.Engine,
        table_name: str,
        schema: str,
        key_cols: list[str],
    ) -> None:
        super().__init__(engine, table_name, schema, key_cols)

    def merge(self, df: pd.DataFrame) -> list[dict]:
        if df is None or df.empty:
            logging.info("[DbMergeHandler] DataFrame is empty — nothing to merge into %s.%s",
                         self.schema, self.table_name)
            return []

        temp       = f"{self.table_name}_tmp_{uuid.uuid4().hex[:12]}"
        columns    = df.columns.tolist()
        non_key    = [c for c in columns if c not in self.key_cols]
        on_clause  = " AND ".join(f"tgt.[{c}] = src.[{c}]" for c in self.key_cols)
        update_set = ", ".join(f"tgt.[{c}] = src.[{c}]" for c in non_key)
        col_list   = ", ".join(f"[{c}]" for c in columns)
        val_list   = ", ".join(f"src.[{c}]" for c in columns)

        merge_sql = f"""
            MERGE [{self.schema}].[{self.table_name}] AS tgt
            USING [{self.schema}].[{temp}] AS src
              ON {on_clause}
            WHEN MATCHED THEN
                UPDATE SET {update_set}
            WHEN NOT MATCHED THEN
                INSERT ({col_list})
                VALUES ({val_list})
            OUTPUT $action AS merge_action, inserted.*;
        """

        try:
            df.to_sql(temp, con=self.engine, schema=self.schema, if_exists="replace", index=False)
            with self.engine.begin() as conn:
                result  = conn.execute(sa.text(merge_sql))
                rows    = result.fetchall()
                keys    = list(result.keys())
            affected = [dict(zip(keys, row)) for row in rows]
            inserted = sum(1 for r in affected if r.get("merge_action") == "INSERT")
            updated  = sum(1 for r in affected if r.get("merge_action") == "UPDATE")
            logging.info("[DbMergeHandler] %s.%s — %d inserted, %d updated",
                         self.schema, self.table_name, inserted, updated)
            return affected
        except Exception:
            logging.exception("[DbMergeHandler] Failed to merge into %s.%s",
                              self.schema, self.table_name)
            raise
        finally:
            self._drop_temp(temp)

    def handle(self, df: pd.DataFrame, dropNa: bool = True, dtype=None,
               created_date_column: str = "CreatedDate") -> list[dict]:
        return self.merge(df)
