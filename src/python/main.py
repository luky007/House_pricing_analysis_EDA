"""Collection of scripts for cleaning and analyzing the input dataset related to the housing market."""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from utils import (
    drop_all_tables,
    execute_sql_file,
    extract_data_from_sql_house,
    load_db,
    merge_data,
    read_csv_data_house,
    read_excel_house_price,
)

import coloredlogs  # type: ignore [import-untyped]
import mysql.connector as myc
from dotenv import load_dotenv
from rich.traceback import install


if TYPE_CHECKING:
    from mysql.connector.abstracts import MySQLConnectionAbstract
    from mysql.connector.pooling import PooledMySQLConnection

load_dotenv()
HOST = os.getenv("HOST")
USER_DB = os.getenv("USER_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
NAME_DB = os.getenv("NAME_DB")


def main() -> None:
    """The main function."""
    install(show_locals=True)
    coloredlogs.install()  # pyright: ignore[reportUnknownMemberType]
    logger = logging.getLogger(Path(__file__).stem)
    logger.setLevel(logging.INFO)
    path_current_folder = Path(__file__).resolve().parent
    path_input_folder = Path(path_current_folder.parent.parent / "input")
    connection: PooledMySQLConnection | MySQLConnectionAbstract = myc.connect(
        host=HOST, user=USER_DB, password=PASSWORD_DB, database=NAME_DB
    )
    (
        list_house_data_wip_01,
        list_house_price_data_wip_01,
    ) = extract_data_from_sql_house(
        path_sql=Path(path_input_folder / "house").with_suffix(".sql")
    )
    list_house_data_wip_02 = read_csv_data_house(
        path_csv=Path(path_input_folder / "data_house").with_suffix(".csv")
    )
    list_house_price_data_wip_02 = read_excel_house_price(
        path_excel=Path(path_input_folder / "house_price").with_suffix(".xls")
    )
    list_house_data = merge_data(
        list_instance_wip_01=list_house_data_wip_01,
        list_instance_wip_02=list_house_data_wip_02,
        list_broken_row={46},
    )
    list_house_price_data = merge_data(
        list_instance_wip_01=list_house_price_data_wip_01,
        list_instance_wip_02=list_house_price_data_wip_02,
        list_broken_row={46},
    )
    drop_all_tables(connection=connection)
    execute_sql_file(
        connection=connection,
        path_sql=Path(path_current_folder.parent / "sql" / "create_tables").with_suffix(
            ".sql"
        ),
    )
    load_db(
        connection=connection,
        list_house_data=list_house_data,
        list_house_price_data=list_house_price_data,
    )


if __name__ == "__main__":
    main()
