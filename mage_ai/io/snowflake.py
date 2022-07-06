from mage_ai.io.base import BaseSQL
from pandas import DataFrame
from snowflake.connector import connect
from snowflake.connector.pandas_tools import write_pandas


class Snowflake(BaseSQL):
    """
    Handles data transfer between a Snowflake data warehouse and the Mage app.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initializes settings for connecting to Snowflake data warehouse.
        The following arguments must be provided to the connector, all other
        arguments are optional.

        Required Arguments:
            user (str): Username for the Snowflake user.
            password (str): Login Password for the user.
            account (str): Snowflake account identifier (excluding
            `snowflake-computing.com` suffix).
        """
        super().__init__(**kwargs)

    def open(self) -> None:
        """
        Opens a connection to Snowflake.
        """
        self._ctx = connect(**self.settings)

    def query(self, query_string: str, **kwargs) -> None:
        """
        Executes any query in the Snowflake data warehouse.

        Args:
            query_string (str): The query to execute on Snowflake's platform.
            **kwargs: Additional parameters to provide to the query
        """
        with self.conn.cursor() as cur:
            return cur.execute(query_string, **kwargs)

    def load(self, query_string: str, *args, **kwargs) -> DataFrame:
        """
        Loads data from Snowflake into a Pandas data frame based on the query given.
        This will fail unless a `SELECT` query is provided.

        Args:
            query_string (str): Query to fetch a table or subset of a table.
            *args, **kwargs: Additional parameters to provide to the query

        Returns:
            DataFrame: Data frame associated with the given query.
        """
        with self.conn.cursor() as cur:
            return cur.execute(query_string, *args, **kwargs).fetch_pandas_all()

    def export(
        self,
        df: DataFrame,
        table_name: str,
        database: str,
        schema: str,
        if_exists: str = 'append',
        **kwargs,
    ) -> None:
        """
        Exports a Pandas data frame to a Snowflake warehouse based on the table name. If table doesn't
        exist, the table is automatically created.

        Args:
            df (DataFrame): Data frame to export to a Snowflake warehouse.
            table_name (str): Name of the table to export data to (excluding database and schema).
            database (str): Name of the database in which the table is located.
            schema (str): Name of the schema in which the table is located.
            if_exists (str, optional): Specifies export policy if table exists. Either
                - `'fail'`: throw an error.
                - `'replace'`: drops existing table and creates new table of same name.
                - `'append'`: appends data frame to existing table.
            Defaults to `'append'`.
            **kwargs: Additional arguments to pass to writer
        """
        exists = False
        with self._ctx.cursor() as cur:
            cur.execute(f'SHOW TABLES LIKE \'{table_name}\' IN SCHEMA {database}.{schema}')
            if cur.rowcount == 1:
                exists = True
            elif cur.rowcount > 1:
                raise ValueError(f'Two or more tables with the name {table_name} are found.')
            if exists:
                if if_exists == 'fail':
                    raise RuntimeError(
                        f'Table {table_name} already exists in the current warehouse, database, schema scenario.'
                    )
                elif if_exists == 'replace':
                    cur.execute(f'DROP TABLE {table_name}')
                elif if_exists != 'append':
                    raise ValueError(
                        f'Invalid policy specified for handling existence of table: \'{if_exists}\''
                    )

        auto_create_table = True
        if 'auto_create_table' in kwargs:
            auto_create_table = kwargs.pop(auto_create_table)
            if auto_create_table is None:
                auto_create_table = True

        write_pandas(
            self.conn,
            df,
            table_name,
            database=database,
            schema=schema,
            auto_create_table=auto_create_table,
            **kwargs,
        )