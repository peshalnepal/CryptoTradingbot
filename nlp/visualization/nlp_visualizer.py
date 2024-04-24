import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix


class NLPVisualizer:
    def __init__(self, **kwargs) -> None:
        self.nlp_df = kwargs.get("data")

    def plot_distribution(self):
        df = self.nlp_df.data

        plt.figure(figsize=(8, 6))
        sns.countplot(x=self.nlp_df.y, data=df)
        plt.title("Distribution of Sentiment Labels")
        plt.xlabel("Sentiment Labels")
        plt.ylabel("Count")
        plt.show()

    def plot_predictions_distribution(self):
        df = self.nlp_df.data
        if "Prediction" not in df:
            raise ValueError(
                "[NLPVisualizer(error = dataframe does not contain 'Prediction' column)]"
            )

        plt.figure(figsize=(8, 6))
        sns.countplot(x="Predictions", data=df)
        plt.title("Distribution of Predicted Sentiment Labels")
        plt.xlabel("Predicted Sentiment Labels")
        plt.ylabel("Count")
        plt.show()

    def plot_confusion_matrix(self):
        df = self.nlp_df.data

        if "Prediction" not in df:
            raise ValueError(
                "[NLPVisualizer(error = dataframe does not contain 'Prediction' column)]"
            )

        y_true = self.nlp_df.y
        y_pred = df["Predictions"]

        cm = confusion_matrix(y_true, y_pred)

        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=self.nlp_df.y.unique(),
            yticklabels=self.nlp_df.y.unique(),
        )
        plt.title("Confusion Matrix")
        plt.xlabel("Predicted Labels")
        plt.ylabel("True Labels")
        plt.show()

    def plot_wordcloud(self):
        pass

    def plot_custom_chart(self):
        pass
