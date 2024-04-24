from sklearn.metrics import classification_report


class NLPLogger:
    def __init__(self, **kwargs) -> None:
        self.df = kwargs.get("data")

        if self.df is None:
            raise ValueError("[NLPLogger(error = No data argument supplied.)]")

    def classification_report(self, **kwargs):
        y_true = kwargs.get("y_true", self.df["Sentiment Encoded"])
        y_pred = kwargs.get("y_pred", self.df["Predictions"])

        report = classification_report(y_true, y_pred)
        print(report)
