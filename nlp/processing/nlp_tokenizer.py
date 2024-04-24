import torch
from tqdm import tqdm
from .nlp_dataframe import NLPDataFrame

from transformers import BertTokenizerFast, RobertaTokenizerFast


class NLPTokenizer:
    def __init__(self, **kwargs) -> None:
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.tokenizer = kwargs.get("tokenizer")

    def __call__(self, **kwargs):
        nlp_df = kwargs.get("nlp_df")
        print(f"[NLPTokenizer(device={self.device}, tokenizer={self.tokenizer})]")
        if isinstance(self.tokenizer, BertTokenizerFast):
            return self.bert_tokenizer_fast(nlp_df)
        if isinstance(self.tokenizer, RobertaTokenizerFast):
            return self.roberta_tokenizer_fast(nlp_df)

    def bert_tokenizer_fast(self, nlp_dataframe: NLPDataFrame):
        tensors = []
        for document in tqdm(nlp_dataframe.X, desc="Tokenizing"):
            tensor = self.tokenizer(document, return_tensors="pt", truncation=True).to(
                self.device
            )
            tensors.append(
                {
                    "input_ids": tensor["input_ids"],
                    "token_type_ids": tensor["token_type_ids"],
                    "attention_mask": tensor["attention_mask"],
                }
            )
        return tensors

    def roberta_tokenizer_fast(self, nlp_dataframe: NLPDataFrame):
        tensors = []
        for document in tqdm(nlp_dataframe.X, desc="Tokenizing"):
            tensor = self.tokenizer(document, return_tensors="pt", truncation=True).to(
                self.device
            )
            tensors.append(
                {
                    "input_ids": tensor["input_ids"],
                    "attention_mask": tensor["attention_mask"],
                }
            )
        return tensors
