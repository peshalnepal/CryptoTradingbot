from .nlp_dataframe import NLPDataFrame


class NLPEncoderFN:
    def __init__(self, **kwargs):
        self.enc_map = kwargs.get("map")
        self.df: NLPDataFrame = kwargs.get("data")

    def __call__(self, **kwargs):
        self.enc_map = kwargs.get("map", self.enc_map)
        self.df: NLPDataFrame = kwargs.get("data", self.df)
        overwrite = kwargs.get("overwrite", False)

        if self.df is None:
            raise ValueError(
                "[EncoderFN(error = 'data' must be passed to __call__ or __init__)]"
            )
        if self.enc_map is None:
            raise ValueError(
                "[EncoderFN(error = 'map' must be passed to __call__ or __init__)]"
            )

        col_name = (
            self.df.sentiment_col if overwrite else f"{self.df.sentiment_col} Encoded"
        )

        self.df[col_name] = self.df[self.df.sentiment_col].map(self.enc_map)
        self.df.y = self.df[col_name]
