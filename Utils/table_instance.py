import pandas as pd
from typing import Optional
from typing_extensions import Self
from functools import lru_cache

class Table:
    """
    A table in a database.

    Args:
        name (str): The name of the table.
        df (pandas.DataFrame): The underlying data frame of the table.
        pkey_col (str, optional): The primary key column if it exists.
            (default: :obj:`None`)
        time_col (str, optional): The time column. (default: :obj:`None`)
    """

    def __init__(
        self,
        name: str,
        df: pd.DataFrame,
        pkey_col: Optional[str] = None,
        time_col: Optional[str] = None,
    ):
        self.df = df
        self.name = name
        self.pkey_col = pkey_col
        self.time_col = time_col

    def __repr__(self) -> str:
        """
        Returns a string representation of the Table object.

        Returns:
            str: The string representation of the Table object.
        """
        return (
            f"Table(df = \n{self.df},\n"
            f"  pkey_col = {self.pkey_col},\n"
            f"  time_col = {self.time_col}"
            f")"
        )

    def __len__(self) -> int:
        """
        Returns the number of rows in the table.

        Returns:
            int: The number of rows in the table.
        """
        return len(self.df)

    def upto(self, time_stamp: pd.Timestamp) -> Self:
        """
        Returns a table with all rows up to the specified time.

        Args:
            time_stamp (pd.Timestamp): The time stamp.

        Returns:
            Table: A new table with all rows up to the specified time.
        """
        if self.time_col is None:
            return self

        return Table(
            df=self.df.query(f"{self.time_col} <= @time_stamp"),
            pkey_col=self.pkey_col,
            time_col=self.time_col,
        )

    @property
    @lru_cache(maxsize=None)
    def min_timestamp(self) -> pd.Timestamp:
        """
        Returns the earliest time in the table.

        Returns:
            pd.Timestamp: The earliest time in the table.

        Raises:
            ValueError: If the table has no time column.
        """
        if self.time_col is None:
            raise ValueError("Table has no time column.")

        return self.df[self.time_col].min()

    @property
    @lru_cache(maxsize=None)
    def max_timestamp(self) -> pd.Timestamp:
        """
        Returns the latest time in the table.

        Returns:
            pd.Timestamp: The latest time in the table.

        Raises:
            ValueError: If the table has no time column.
        """
        if self.time_col is None:
            raise ValueError("Table has no time column.")

        return self.df[self.time_col].max()