from transformers import AutoTokenizer, AutoModelForSequenceClassification

from models import NLPModel
from processing import (
    NLPLabelEncoder,
    NLPEncoderFN,
    NLPPostProcessor,
    NLPDataFrameWriter,
    NLPDataFrame,
    NLPTokenizer,
)

from visualization import NLPVisualizer


def finbert_01():
    df = NLPDataFrame(temp_file="predictions_1703229443.csv.gz", text_col="Sentence")
    df.load()

    encoder = NLPLabelEncoder(chain=[NLPEncoderFN()])
    encoder(
        data=df,
        map={
            "positive": 0,
            "negative": 1,
            "neutral": 2,
        },
    )

    if "Prediction" not in df.data:
        tokenizer = NLPTokenizer(
            tokenizer=AutoTokenizer.from_pretrained("ProsusAI/finbert")
        )
        tensors = tokenizer(df)

        model = NLPModel(
            model=AutoModelForSequenceClassification.from_pretrained(
                "ProsusAI/finbert"
            ),
            is_auto_model=True,
        )
        predictions = model(tensors=tensors)

        postprocessor = NLPPostProcessor(chain=["set", NLPDataFrameWriter()])
        postprocessor(predictions=predictions, data=df)

    visualizer = NLPVisualizer(data=df)
    visualizer.plot_distribution()
    visualizer.plot_predictions_distribution()
    visualizer.plot_confusion_matrix()

    logger = NLPLogger(data=df)
    logger.classification_report()
