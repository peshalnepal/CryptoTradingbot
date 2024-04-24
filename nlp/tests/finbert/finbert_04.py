from models import NLPModel

from visualization import NLPVisualizer

from processing import (
    NLPLabelEncoder,
    NLPEncoderFN,
    NLPPostProcessor,
    NLPDataFrameWriter,
    NLPDataFrame,
    NLPTokenizer,
    NLPLogger,
)

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import load_dataset


def finbert_03():
    # hf_ds = load_dataset(
    #     "zeroshot/twitter-financial-news-sentiment",
    #     split="train",
    # )

    # print(hf_ds)
    # print(hf_ds["text"])
    # print(hf_ds["label"])

    nlp_df = NLPDataFrame(
        temp_file="predictions_1703231943.csv.gz", text_col="Sentence"
    )
    nlp_df.load()

    encoder = NLPLabelEncoder(chain=[NLPEncoderFN()])
    encoder(
        data=nlp_df,
        map={
            1: 0,
            0: 1,
            2: 2,
        },
    )

    if "Prediction" not in nlp_df.data:
        tokenizer = NLPTokenizer(
            tokenizer=AutoTokenizer.from_pretrained(
                "ahmedrachid/FinancialBERT-Sentiment-Analysis", num_labels=3
            )
        )
        tensors = tokenizer(data=nlp_df)

        model = NLPModel(
            model=AutoModelForSequenceClassification.from_pretrained(
                "ahmedrachid/FinancialBERT-Sentiment-Analysis"
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
