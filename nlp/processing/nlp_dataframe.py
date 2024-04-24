import pandas as pd
import numpy as np
import datasets as hf
from .nlp_dataframe_loader import NLPDataFrameLoader


class NLPDataFrame:
    def __init__(self, **kwargs) -> None:
        self.n_cat = None
        self.y = None
        self.X = None
        self.data: pd.DataFrame | hf.Dataset = kwargs.get("data")
        self.loader = NLPDataFrameLoader(**kwargs)
        self.text_col = kwargs.get("text_col", "Text")
        self.sentiment_col = kwargs.get("sentiment_col", "Sentiment")
        self.timestamp_col = kwargs.get("timestamp_col", "Timestamp")

        if isinstance(self.data, pd.DataFrame):
            self.load_df(df=self.data)
            
        print(f"[{self}] __init__: shape - {self.data.shape}")

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value) -> None:
        self.data[key] = value

    def load(self, **kwargs) -> "NLPDataFrame":
        if isinstance(self.data, hf.Dataset):
            print(f"[NLPDataFrame(load = Loading from hugging face dataset)]")
            self.load_hf(**kwargs)

        if isinstance(kwargs.get("df"), list):
            print(f"[NLPDataFrame(load = Loading from pandas dataframe)]")
            self.load_df(**kwargs)

        if self.data is None:
            print(f"[NLPDataFrame(load = Loading from local .csv file)]")
            self.load_local(**kwargs)

        print(f"[{self}] load: shape - {self.data.shape}")
        return self

    def load_dict(self, **kwargs):
        print(f"[NLPDataFrame] Loading data from API Inputs")
        self.data = pd.DataFrame([vars(input) for input in kwargs.get("df")])
        x_col = kwargs.get("x", self.text_col.lower())
        y_col = kwargs.get("y", self.sentiment_col.lower())

        self.X = self.data[x_col]
        self.y = self.data[y_col]
        self.n_cat = len(self.y.unique())

    def load_df(self, **kwargs):
        """load_df requires y_col and data to be set manually, or it can be ran without
        to make predictions
        """
        print(f"[NLPDataFrame] Loading data from API Inputs")
        self.data = kwargs.get("df")
        x_col = kwargs.get("x", self.text_col)
        self.X = self.data[x_col]

    def load_hf(self, **kwargs):
        dataset = self.data
        x_col = kwargs.get("x", "sentence")
        y_col = kwargs.get("y", "label")

        sentences = dataset[x_col]
        labels = dataset[y_col]

        if not isinstance(sentences, list):
            raise TypeError(
                f"[NLPDataFrame(error = dataset['{x_col}'] is not type list in hugging face dataframe)]"
            )
        if not isinstance(labels, list):
            raise TypeError(
                f"[NLPDataFrame(error = dataset['{y_col}'] is not type list in hugging face dataframe)]"
            )

        self.data = pd.DataFrame(
            data={
                f"{self.text_col}": sentences,
                f"{self.sentiment_col}": labels,
            },
        )
        print(self.data)
        self.X = self.data[self.text_col]
        self.y = self.data[self.sentiment_col]
        self.n_cat = len(self.y.unique())

    def load_local(self, **kwargs):
        filename = kwargs.get("filename", "stock_data.csv")
        text_col = kwargs.get("text_col", self.text_col)
        sentiment_col = kwargs.get("sentiment_col", self.sentiment_col)

        if not isinstance(filename, str):
            raise TypeError("[NLPDataFrame(error = filename is not type str)]")
        if not isinstance(text_col, str):
            raise TypeError("[NLPDataFrame(error = text_col is not type str)]")
        if not isinstance(sentiment_col, str):
            raise TypeError("[NLPDataFrame(error = sentiment_col is not type str)]")

        self.data = self.loader.read(**kwargs)
        print(self.data)
        self.X = self.data[text_col]
        self.y = self.data[sentiment_col]
        self.n_cat = len(self.y.unique())

    def set_predictions(self, y_pred: np.ndarray) -> None:
        print(f"[{self}] set_predictions: y_pred shape - {y_pred.shape}")
        if "Prediction" in self.data:
            self.data.drop("Prediction", axis=1)
        self.data["Prediction"] = y_pred

    def reshape(self, shape_fn, **kwargs) -> None:
        if "Prediction" not in self.data:
            print("Please run set_predictions() first")
            return

        self.data = shape_fn(data=self)
        unique_sentiments = self["Sentiment"].unique()
        unique_predictions = self["Predictions"].unique()
        print(
            f"[NLPDataFrame(unique_sentiments={unique_sentiments}, unique_predictions={unique_predictions})]"
        )
