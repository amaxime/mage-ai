from mage_ai.data_loader.bigquery import BigQuery
from pandas import DataFrame


@data_loader
def load_data_from_big_query() -> DataFrame:
    """
    Template code for loading data from Google BigQuery.

    Depending on your preferred method of providing service account credentials,
    there are three options for initializing a Google BigQuery data loader:

    1. (Default) If the environment variable `GOOGLE_APPLICATION_CREDENTIALS` contains the path
    to the service account key, construct the data loader using the default constructor. Any
    additional parameters can still be specified as a keyword argument.

    2. If the path to the service account key is manually specified, construct the data loader
    using the factory method `with_credentials_file`. Example:
    ```
    BigQuery.with_credentials_file('path/to/service/account/key.json', **kwargs)
    ```

    3. If the contents of the service account key are manually specified in a dictionary-like
    object, construct the data loader using this factory method `with_credentials_object`. Example:
    ```
    BigQuery.with_credentials_object({'service_key': ...}, **kwargs)
    ```
    """

    query = 'your_gbq_query'
    config = {
        # Specify any other configuration settings here to pass to BigQuery client
        'project': 'your_project_name',
    }
    return BigQuery(**config).load(query)