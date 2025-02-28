from typing import Dict

from airflow.exceptions import AirflowException

from astro.constants import Database
from astro.sql.operators.sql_decorator import SqlDecoratedOperator
from astro.sql.table import Table
from astro.utils.bigquery_merge_func import bigquery_merge_func
from astro.utils.database import get_database_from_conn_id
from astro.utils.postgres_merge_func import postgres_merge_func
from astro.utils.schema_util import (
    get_error_string_for_multiple_dbs,
    tables_from_same_db,
)
from astro.utils.snowflake_merge_func import snowflake_merge_func
from astro.utils.sqlite_merge_func import sqlite_merge_func
from astro.utils.task_id_helper import get_unique_task_id


class SqlMergeOperator(SqlDecoratedOperator):
    template_fields = ("target_table", "merge_table")

    def __init__(
        self,
        target_table: Table,
        merge_table: Table,
        merge_keys,
        target_columns,
        merge_columns,
        conflict_strategy,
        **kwargs,
    ):
        self.target_table = target_table
        self.merge_table = merge_table
        self.merge_keys = merge_keys
        self.target_columns = target_columns
        self.merge_columns = merge_columns
        self.conflict_strategy = conflict_strategy
        task_id = get_unique_task_id("merge_table")

        def null_function():
            pass

        super().__init__(
            raw_sql=True,
            parameters={},
            task_id=kwargs.get("task_id") or task_id,
            op_args=(),
            python_callable=null_function,
            **kwargs,
        )

    def execute(self, context: Dict):
        self.database = self.target_table.database
        self.conn_id = self.target_table.conn_id
        self.schema = self.target_table.schema
        self.warehouse = self.target_table.warehouse
        if not tables_from_same_db([self.target_table, self.merge_table]):
            raise ValueError(
                get_error_string_for_multiple_dbs([self.target_table, self.merge_table])
            )

        database = get_database_from_conn_id(self.conn_id)
        if database in (Database.POSTGRES, Database.POSTGRESQL):
            self.sql = postgres_merge_func(
                target_table=self.target_table,
                merge_table=self.merge_table,
                merge_keys=self.merge_keys,
                target_columns=self.target_columns,
                merge_columns=self.merge_columns,
                conflict_strategy=self.conflict_strategy,
            )
        elif database == Database.SQLITE:
            self.sql = sqlite_merge_func(
                target_table=self.target_table,
                merge_table=self.merge_table,
                merge_keys=self.merge_keys,
                target_columns=self.target_columns,
                merge_columns=self.merge_columns,
                conflict_strategy=self.conflict_strategy,
            )
        elif database == Database.SNOWFLAKE:
            self.sql, self.parameters = snowflake_merge_func(
                target_table=self.target_table,
                merge_table=self.merge_table,
                merge_keys=self.merge_keys,
                target_columns=self.target_columns,
                merge_columns=self.merge_columns,
                conflict_strategy=self.conflict_strategy,
            )
        elif database == Database.BIGQUERY:
            self.sql, self.parameters = bigquery_merge_func(
                target_table=self.target_table,
                merge_table=self.merge_table,
                merge_keys=self.merge_keys,
                target_columns=self.target_columns,
                merge_columns=self.merge_columns,
                conflict_strategy=self.conflict_strategy,
            )
        else:
            raise AirflowException("Please pass a postgres conn id")
        super().execute(context)
        return self.target_table
