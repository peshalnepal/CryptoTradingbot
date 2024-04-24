from flask import Flask
from flask_cors import CORS
from config import Config


class Cors:
    def __init__(self, server: Flask, config: Config):
        CORS(
            server,
            supports_credentials=True,
            origins=[config.origin(), "http://localhost:8080"],
            methods=["POST", "GET", "OPTIONS"],
            allow_headers=[
                "Access-Control-Allow-Credentials",
                "Access-Control-Allow-Headers",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Origin",
                "Content-Type",
            ],
        )
