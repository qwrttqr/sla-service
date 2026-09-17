import io
import pandas as pd

from fastapi import UploadFile


class CsvParser:
    @staticmethod
    async def parse_from_network(
        files: list[UploadFile],
        encoding: str
    ) -> pd.DataFrame:
        df_list = []

        for file in files:
            contents = await file.read()

            parsed_df = pd.read_csv(io.BytesIO(contents), sep=';', encoding=encoding)

            df_list.append(parsed_df)

            await file.close()

        if df_list:
            return pd.concat(df_list, ignore_index=True)

        return pd.DataFrame()

    @staticmethod
    async def parse_from_disk(
        file_paths: list[str],
        encoding: str
    ) -> pd.DataFrame:
        df_list = []

        for file_path in file_paths:
            parsed_df = pd.read_csv(file_path, sep=';', encoding=encoding)

            df_list.append(parsed_df)

        if df_list:
            return pd.concat(df_list, ignore_index=True)

        return pd.DataFrame()
