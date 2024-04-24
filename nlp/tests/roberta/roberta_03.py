from processing import (
    NLPLabelEncoder,
    NLPEncoderFN,
    NLPPostProcessor,
    NLPDataFrameWriter,
    NLPDataFrame,
    NLPTokenizer,
    NLPLogger,
)
from models import NLPModel
from visualization import NLPVisualizer

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datasets import load_dataset


def roberta_03():
    hf_ds = load_dataset(
        "zeroshot/twitter-financial-news-sentiment",
        split="train",
    )

    nlp_df = NLPDataFrame(hf_ds=hf_ds)
    nlp_df.load(x="text")

    encoder = NLPLabelEncoder(chain=[NLPEncoderFN()])
    encoder(
        data=nlp_df,
        map={
            0: 0,
            2: 1,
            1: 2,
        },
    )

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
