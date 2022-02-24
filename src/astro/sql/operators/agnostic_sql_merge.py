"""
Copyright Astronomer, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Dict, Union

from airflow.exceptions import AirflowException
from airflow.hooks.base import BaseHook

from astro.sql.operators.sql_decorator import SqlDecoratoratedOperator
from astro.sql.table import Table, TempTable
from astro.utils.bigquery_merge_func import bigquery_merge_func
from astro.utils.postgres_merge_func import postgres_merge_func
from astro.utils.schema_util import (
    get_error_string_for_multiple_dbs,
    get_schema,
    tables_from_same_db,
)
from astro.utils.snowflake_merge_func import snowflake_merge_func
from astro.utils.sqlite_merge_func import sqlite_merge_func
from astro.utils.task_id_helper import get_unique_task_id


class SqlMergeOperator(SqlDecoratoratedOperator):
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

        if not tables_from_same_db([target_table, merge_table]):
            raise ValueError(
                get_error_string_for_multiple_dbs([target_table, merge_table])
            )

        def null_function():
            pass

        super().__init__(
            raw_sql=True,
            parameters={},
            task_id=kwargs.get("task_id") or task_id,
            op_args=(),
            python_callable=null_function,
            database=self.target_table.database,
            conn_id=self.target_table.conn_id,
            schema=self.target_table.schema,
            warehouse=self.target_table.warehouse,
            **kwargs,
        )

    def execute(self, context: Dict):
        self._set_default_values_from_dag_default(context)
        conn_type = BaseHook.get_connection(self.conn_id).conn_type  # type: ignore
        if conn_type == "postgres":
            self.sql = postgres_merge_func(
                target_table=self.target_table,
                merge_table=self.merge_table,
                merge_keys=self.merge_keys,
                target_columns=self.target_columns,
                merge_columns=self.merge_columns,
                conflict_strategy=self.conflict_strategy,
            )
        elif conn_type == "sqlite":
            self.sql = sqlite_merge_func(
                target_table=self.target_table,
                merge_table=self.merge_table,
                merge_keys=self.merge_keys,
                target_columns=self.target_columns,
                merge_columns=self.merge_columns,
                conflict_strategy=self.conflict_strategy,
            )
        elif conn_type == "snowflake":
            self.sql, self.parameters = snowflake_merge_func(
                target_table=self.target_table,
                merge_table=self.merge_table,
                merge_keys=self.merge_keys,
                target_columns=self.target_columns,
                merge_columns=self.merge_columns,
                conflict_strategy=self.conflict_strategy,
            )
        elif conn_type == "bigquery":
            self.sql, self.parameters = bigquery_merge_func(
                target_table=self.target_table,
                merge_table=self.merge_table,
                merge_keys=self.merge_keys,
                target_columns=self.target_columns,
                merge_columns=self.merge_columns,
                conflict_strategy=self.conflict_strategy,
            )
        else:
            raise AirflowException(f"please give a postgres conn id")

        return super().execute(context)

    def _set_default_values_from_dag_default(self, context):
        self.schema = self.schema or get_schema(context)
        if context.get("dag"):
            self.conn_id = self.conn_id or context["dag"].default_args.get("conn_id")
            self.database = self.database or context["dag"].default_args.get("database")
            self.warehouse = self.warehouse or context["dag"].default_args.get(
                "warehouse"
            )
            self.role = self.role or context["dag"].default_args.get("role")
