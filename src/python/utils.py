"""Collections of utility functions."""
import csv
import logging
import re
from dataclasses import fields
from pathlib import Path
from typing import TypeVar, cast, overload

from dataclasses_house import HouseData, HousePriceData

import pandas as pd
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection


def read_csv_data_house(path_csv: Path) -> list[HouseData]:
    """Read the input .csv file given.

    Returns:
        list[HouseData]: a list containing HouseData instances.
    """
    list_house_data: list[HouseData] = []
    with open(path_csv, encoding="UTF-8") as file:
        csv_reader = csv.DictReader(file, delimiter=",")
        for _, row in enumerate(csv_reader, start=1):
            (
                furnishing_status,
                house_id,
                n_bathroom,
                n_stories,
                n_parking,
                is_mainroad,
                has_guestroom,
                has_hot_water,
                has_air_conditioning,
                is_pref_area,
                has_basement,
            ) = (
                row["furnishingstatus"],
                int(row["id"]),
                int(row["bathrooms"]),
                int(row["stories"]),
                int(row["parking"]),
                row["mainroad"] == "yes",
                row["guestroom"] == "yes",
                row["hotwaterheating"] == "yes",
                row["airconditioning"] == "yes",
                row["prefarea"] == "yes",
                row["basement"] == "yes",
            )
            furnishing_id: int = 0
            if furnishing_status == "semi-furnished":
                furnishing_id = 2
            elif furnishing_status == "unfurnished":
                furnishing_id = 1
            elif furnishing_status == "furnished":
                furnishing_id = 0
            list_house_data.append(
                HouseData(
                    house_id=house_id,
                    n_bathroom=n_bathroom,
                    n_stories=n_stories,
                    is_mainroad=is_mainroad,
                    has_guestroom=has_guestroom,
                    has_hot_water=has_hot_water,
                    has_air_conditioning=has_air_conditioning,
                    n_parking_slot=n_parking,
                    is_pref_area=is_pref_area,
                    has_basement=has_basement,
                    furnishing_id=furnishing_id,
                )
            )
        return list_house_data


def read_excel_house_price(path_excel: Path) -> list[HousePriceData]:
    """Read the input excel.

    Args:
        path_excel (Path): the path of the input excel.

    Returns:
        list[HousePriceData]: a list of HousePriceData instances.
    """
    list_house_price_data: list[HousePriceData] = []
    df_house_price_data = pd.read_excel(path_excel)  # type: ignore
    price_values: list[int] = df_house_price_data["price"]  # type: ignore
    for i, price in enumerate(price_values):
        list_house_price_data.append(HousePriceData(house_id=i, price=price))
    return list_house_price_data


def extract_data_from_sql_house(
    path_sql: Path,
) -> tuple[list[HouseData], list[HousePriceData]]:
    """Extract the data from the input SQL data.

    Args:
        path_sql (Path): the path of the file .sql to read

    Returns:
        tuple[list[HouseData], list[HousePriceData]]: list containing merged instances.
    """
    list_house_data: list[HouseData] = []
    list_house_price_data: list[HousePriceData] = []
    with open(path_sql, encoding="UTF-8") as f:
        sql_create_tables = f.read()

    # for sql_command in sql_create_tables.split(";"):
    matches = re.finditer(
        r"INSERT INTO `` \(`house_ID`,`area`,`bedrooms`\)\s+VALUES \((\d+),(\d+),(\d+)\);",
        sql_create_tables,
    )
    for match in matches:
        if match:
            house_id = int(match.group(1)) - 1
            area = int(match.group(2))
            bedrooms = int(match.group(3))
            list_house_price_data.append(HousePriceData(house_id=house_id, area=area))
            list_house_data.append(HouseData(house_id=house_id, n_bedroom=bedrooms))
    return list_house_data, list_house_price_data


def load_db(
    connection: PooledMySQLConnection | MySQLConnectionAbstract,
    list_house_data: list[HouseData],
    list_house_price_data: list[HousePriceData],
) -> None:
    """Load the data inside the mySQL db.

    Args:
        connection (PooledMySQLConnection | MySQLConnectionAbstract): the connection to use.
        list_house_data (list[HouseData]): list containing the instances HouseData.
        list_house_price_data (list[HousePriceData]): list containing the instances HousePriceData.
    """
    logger = logging.getLogger(Path(__file__).stem)
    with connection.cursor() as cursor:
        for data in list_house_data:
            cursor.execute(
                "INSERT INTO house_data (house_id, n_bedroom, n_bathroom, n_stories, \
                      is_mainroad, has_guestroom, has_basement, has_hot_water, \
                        has_air_conditioning, n_parking_slot, is_pref_area, furnishing_id) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    data.house_id,
                    data.n_bedroom,
                    data.n_bathroom,
                    data.n_stories,
                    data.is_mainroad,
                    data.has_guestroom,
                    data.has_basement,
                    data.has_hot_water,
                    data.has_air_conditioning,
                    data.n_parking_slot,
                    data.is_pref_area,
                    data.furnishing_id,
                ),
            )
        connection.commit()

    with connection.cursor() as cursor:
        for data in list_house_price_data:
            cursor.execute(
                "INSERT INTO house_price_data (house_id, price, area) \
                VALUES (%s, %s, %s)",
                (data.house_id, data.price, data.area),
            )
        connection.commit()

    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO furnishing_status (furnishing_id, furnishing_status) \
            VALUES (%s, %s)",
            (0, "furnished"),
        )
        cursor.execute(
            "INSERT INTO furnishing_status (furnishing_id, furnishing_status) \
            VALUES (%s, %s)",
            (1, "unfurnished"),
        )
        cursor.execute(
            "INSERT INTO furnishing_status (furnishing_id, furnishing_status) \
            VALUES (%s, %s)",
            (2, "semi-furnished"),
        )
        connection.commit()
    logger.info("Successfully loaded data into the DB")


T = TypeVar("T")


def merge_dataclasses(instance1: T, instance2: T) -> T:
    """Merges two instances of the same data class by taking non-None values from either instance.

    Args:
        instance1 (T): The first input instance.
        instance2 (T): The second input instance.

    Raises:
        TypeError: The instances do not share the same class type.

    Returns:
        T: Return the instances with the value merged from each others
    """
    if not isinstance(instance1, type(instance2)):
        raise TypeError("Instances must be of the same data class type")

    merged_data = {}
    for field in fields(instance1):  # type: ignore
        value1 = getattr(instance1, field.name)
        value2 = getattr(instance2, field.name)
        merged_data[field.name] = value1 if value1 is not None else value2

    return type(instance1)(**merged_data)


@overload
def merge_data(
    list_instance_wip_01: list[HouseData],
    list_instance_wip_02: list[HouseData],
    list_broken_row: set[int],
) -> list[HouseData]:
    pass


@overload
def merge_data(
    list_instance_wip_01: list[HousePriceData],
    list_instance_wip_02: list[HousePriceData],
    list_broken_row: set[int],
) -> list[HousePriceData]:
    pass


def merge_data(
    list_instance_wip_01: list[HouseData] | list[HousePriceData],
    list_instance_wip_02: list[HouseData] | list[HousePriceData],
    list_broken_row: set[int],
) -> list[HouseData] | list[HousePriceData]:
    """Merge two list that contains the dataclasses defined into one.

    Args:
        list_instance_wip_01 (list[HouseData] | list[HousePriceData]): The first list
          containing the instance to merge.
        list_instance_wip_02 (list[HouseData] | list[HousePriceData]): The second list
          containing the instance to merge.
        list_broken_row (set[int]): contains the house_id to drop.

    Raises:
        ValueError: raise an error in case the house_id of the two instances do not match.

    Returns:
        list[HouseData | HousePriceData]: a list containing the instances with the values merged.
    """
    list_instances_merged: list[HouseData | HousePriceData] = []
    for x, y in zip(list_instance_wip_01, list_instance_wip_02):
        if x.house_id != y.house_id:
            raise ValueError("The id do not match.")
        if x.house_id in list_broken_row:
            continue
        list_instances_merged.append(merge_dataclasses(x, y))
    if isinstance(list_instances_merged[0], HouseData):
        return cast(list[HouseData], list_instances_merged)
    return cast(list[HousePriceData], list_instances_merged)


def drop_all_tables(
    connection: PooledMySQLConnection | MySQLConnectionAbstract,
) -> None:
    """Drop all the tables created previously.

    Args:
        connection (PooledMySQLConnection | MySQLConnectionAbstract): the connection to use.
    """
    logger = logging.getLogger(Path(__file__).stem)
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS house_price_data;")
        cursor.execute("DROP TABLE IF EXISTS furnishing_status;")
        cursor.execute("DROP TABLE IF EXISTS house_data;")
        connection.commit()
    logger.info("Dropped all table in the DB")


def execute_sql_file(
    connection: PooledMySQLConnection | MySQLConnectionAbstract, path_sql: Path
) -> None:
    """Read and execute the sql query within an input file.

    Args:
        connection (PooledMySQLConnection | MySQLConnectionAbstract): the connection to use.
        path_sql (Path): the path of the file .sql to read and execute
    """
    logger = logging.getLogger(Path(__file__).stem)
    with open(path_sql, encoding="UTF-8") as f:
        sql_create_tables = f.read()
    with connection.cursor() as cursor:
        for sql_command in sql_create_tables.split(";"):
            if sql_command.strip():
                cursor.execute(sql_command.strip(), multi=True)
        connection.commit()
    logger.info("Executed sql file: %s", path_sql.name)
