import torch
import numpy as np
from tqdm import tqdm


class NLPModel:
    def __init__(self, **kwargs) -> None:
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model = kwargs.get("model")

        is_auto_model = kwargs.get("is_auto_model", False)
        if is_auto_model:
            self.model = self.model.to(self.device)

        self.y_pred = np.array([])

    def __call__(self, **kwargs) -> np.ndarray:
        print(f"[CryptoBotNLPModel(device={self.device}, model={self.model})]")

        in_place = kwargs.get("in_place", False)
        tensors: list[torch.Tensor] = kwargs.get("tensors")

        with torch.no_grad(), tqdm(total=len(tensors), desc="Predicting") as pbar:
            for tensor in tensors:
                output = self.model(**tensor)
                prediction = torch.argmax(output.logits, dim=1).item()
                self.y_pred = np.append(self.y_pred, prediction)
                pbar.update(1)

        y_pred = self.y_pred
        self.y_pred = np.array([])

        if in_place is False:
            return y_pred

        df = kwargs.get("df")
        df.set_predictions(y_pred)
