import os
import torch

class Config:
    __prod = True if os.getenv("PRODUCTION") == "production" else False
    __origin = (
        "https://crypto-trading-bot.onrender.com" if __prod else "http://localhost:3000"
    )

    def __init__(self) -> None:
        print(f"[CRYPTO BOT SERVER]: Production - {self.__prod}")
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch.set_default_device(device)
        torch.set_default_dtype(torch.float)

    def is_prod(self) -> bool:
        return self.__prod

    def origin(self) -> str:
        return self.__origin

    def cores(self) -> int:
        return os.cpu_count()
