from .nlp_encoder_fn import NLPEncoderFN


class NLPLabelEncoder:
    def __init__(self, chain):
        self.chain = chain

    def __call__(self, **kwargs):
        for fn in self.chain:
            print(f"[NLPLabelEncoder(exec = {fn})]")

            if isinstance(fn, NLPEncoderFN):
                fn(**kwargs)
