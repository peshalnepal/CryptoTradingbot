import json
import os


class Credentials:

    def __init__(self, key) -> None:
        self.key = key

    def load(self, file_name="/keys.json") -> str:
        cwd = os.getcwd()
        path = f"{cwd}{file_name}"

        print(f"Trying to open credentials: [{path}]")

        try:
            with open(path) as file:
                return json.load(file)[self.key]
        except Exception as e:
            print(e)
