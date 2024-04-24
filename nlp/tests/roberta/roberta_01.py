from transformers import AutoTokenizer, AutoModelForSequenceClassification

from models import NLPModel
from processing import (
    NLPLabelEncoder,
    NLPEncoderFN,
    NLPPostProcessor,
    NLPDataFrameWriter,
    NLPDataFrame,
    NLPTokenizer,
    NLPLogger,
)
from visualization import NLPVisualizer


def roberta_01():
    nlp_df = NLPDataFrame(
        temp_file="predictions_1703308445.csv.gz", text_col="Sentence"
    )
    nlp_df.load()

    encoder = NLPLabelEncoder(chain=[NLPEncoderFN()])
    encoder(
        data=nlp_df,
        map={
            "positive": 2,
            "negative": 0,
            "neutral": 1,
        },
    )

    if "Prediction" not in nlp_df.data:
        tokenizer = NLPTokenizer(
            tokenizer=AutoTokenizer.from_pretrained(
                "cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        )
        tensors = tokenizer(data=nlp_df)

        model = NLPModel(
            model=AutoModelForSequenceClassification.from_pretrained(
                "cardiffnlp/twitter-roberta-base-sentiment-latest"
            ),
            is_auto_model=True,
        )
        predictions = model(tensors=tensors)

        postprocessor = NLPPostProcessor(chain=["set", NLPDataFrameWriter()])
        postprocessor(data=nlp_df, predictions=predictions)

    visualizer = NLPVisualizer(data=nlp_df)
    visualizer.plot_distribution()
    visualizer.plot_predictions_distribution()
    visualizer.plot_confusion_matrix()

    logger = NLPLogger(data=nlp_df)
    logger.classification_report()

    print(nlp_df.data.head())
