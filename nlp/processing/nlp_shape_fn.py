import numpy as np


class NLPShapeFN:
    def __init__(self, **kwargs):
        pass

    # Must return a dataframe where Predictions matches the target label
    def __call__(self, **kwargs):
        pass


class FinbertShapeFN(NLPShapeFN):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, **kwargs):
        upper = kwargs.get("upper", 2)
        df = kwargs.get("data", None).data
        if df == None:
            raise ValueError("Data value cannot be None")

        df = df[df["Predictions"] != 0]
        df.loc[:, "Predictions"] = np.where(df["Predictions"] >= upper, 1, -1)
        return df
