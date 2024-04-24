from models import NLPModel
from visualization import NLPVisualizer

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import load_dataset

from processing import (
    NLPPostProcessor,
    NLPDataFrameWriter,
    NLPDataFrame,
    NLPTokenizer,
    NLPLogger,
)


def roberta_02():
    # hf_ds = load_dataset(
    #     "zeroshot/twitter-financial-news-sentiment",
    #     split="train",
    # )

    nlp_df = NLPDataFrame(
        temp_file="predictions_1703233533.csv.gz", text_col="Sentence"
    )
    nlp_df.load(x="text")

    # encoder = NLPLabelEncoder(chain=[NLPEncoderFN()])
    # encoder(
    #     data=nlp_df,
    #     map={
    #         2: 0,
    #         0: 1,
    #         1: 2,
    #     },
    # )

    if "Prediction" not in nlp_df.data:
        tokenizer = NLPTokenizer(
            tokenizer=AutoTokenizer.from_pretrained(
                "cardiffnlp/twitter-roberta-base-sentiment"
            )
        )
        tensors = tokenizer(data=nlp_df)

        model = NLPModel(
            model=AutoModelForSequenceClassification.from_pretrained(
                "cardiffnlp/twitter-roberta-base-sentiment"
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
