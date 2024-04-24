from models import nlp_model
from visualization import NLPVisualizer

from transformers import AutoTokenizer, AutoModelForSequenceClassification

from processing import (
    NLPLabelEncoder,
    NLPEncoderFN,
    NLPPostProcessor,
    NLPDataFrameWriter,
    NLPDataFrame,
    NLPTokenizer,
    NLPLogger,
)

# from datasets import load_dataset


def finbert_02():
    # Supply NLPDataFrame `hf_ds` instead of `temp_file`
    # NLPDataFrame(hf_ds=)
    # hf_ds = load_dataset("financial_phrasebank", "sentences_50agree", split="train", data_dir="./.crypto-bot-nlp/cache/")

    nlp_df = NLPDataFrame(
        temp_file="predictions_1703230127.csv.gz", text_col="Sentence"
    )
    nlp_df.load()

    encoder = NLPLabelEncoder(chain=[NLPEncoderFN()])
    encoder(
        data=nlp_df,
        map={
            2: 0,
            0: 1,
            1: 2,
        },
    )

    if "Prediction" not in nlp_df.data:
        tokenizer = NLPTokenizer(
            tokenizer=AutoTokenizer.from_pretrained("ProsusAI/finbert")
        )
        tensors = tokenizer(data=nlp_df)

        model = nlp_model(
            model=AutoModelForSequenceClassification.from_pretrained(
                "ProsusAI/finbert"
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
