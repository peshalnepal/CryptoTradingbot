from .nlp_dataframe_writer import NLPDataFrameWriter
from .nlp_shape_fn import NLPShapeFN
from .nlp_dataframe import NLPDataFrame
from numpy import ndarray

from time import time


class NLPPostProcessor:
    def __init__(self, **kwargs) -> None:
        self.path = kwargs.get("path", "./data/temp/")
        self.filename = f"predictions_{time()}.tar.gz"
        self.chain = kwargs.get("chain", [])
        self.flags = {"write": True}

    def __call__(self, **kwargs):
        data = kwargs.get("nlp_df")
        predictions = kwargs.get("predictions")

        for fn in self.chain:
            # 1. Set predictions.
            if fn == "set":
                self.set_predictions(data, predictions)

            # 1.1 If writer exists, write original prediction df to a file.
            if isinstance(fn, NLPDataFrameWriter):
                self.write(fn)

            # 2. if Shape function exists, reshape.
            if isinstance(fn, NLPShapeFN):
                self.reshape(fn)

    def set_predictions(self, data: NLPDataFrame, predictions: ndarray) -> None:
        if predictions is None:
            raise ValueError("[NLPPostProcessor(error = No predictions provided)]")

        data.set_predictions(predictions)

    def reshape(self, data: NLPDataFrame, shape_fn: NLPShapeFN):
        data.reshape(shape_fn)

    def write(self, writer):
        if not self.flags["write"]:
            print(
                "[NLPDataFrameWriter(flag = write flag is false, not caching predictions)]"
            )
            return

        path, filename = writer(data=self.data, path="./data/temp/")
        self.path = path
        self.filename = filename
        print(
            f"""[NLPPostProcessor(path="{path}", filename="{filename}")]
 - wrote predictions to "{path}{filename}",
load with NLPDataFrame(temp_file="{filename}")
        """
        )
