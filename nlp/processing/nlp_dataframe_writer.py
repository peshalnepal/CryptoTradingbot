from time import time
from .nlp_dataframe import NLPDataFrame


class NLPDataFrameWriter:
    def __init__(self):
        self.parquet = None

    def __call__(self, data: NLPDataFrame, **kwargs):
        df = data.data

        filename = kwargs.get("filename", f"predictions_{int(time())}.csv.gz")
        path = kwargs.get("path", "./data/temp/")

        df.to_csv(f"{path}{filename}", index=False, compression="gzip")
        return path, filename
