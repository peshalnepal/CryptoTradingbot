from typing import Any
from concurrent.futures import ThreadPoolExecutor, Future, wait
from time import time
from multiprocessing.pool import Pool
from apscheduler.schedulers.background import BaseScheduler
from config import Config
from sockets import SocketServer
from db import Database
from pipelines import Pipeline
from apis import INewsAPI


class Engine:

    # Pipelines are run at a given interval, using Pipeline.exec() function

    __pipelines__: dict[str, Pipeline] = None

    # db - Database
    # reports_api = ReportsAPI
    #
    __context__: dict[str, Any] = None

    __type_map__: dict = {
        "db": Database,
        "reports_api": INewsAPI,
        "threads": ThreadPoolExecutor,
        "pool": Pool,
        "config": Config,
        "socket_server": SocketServer,
        "scheduler": BaseScheduler,
        "service_provider": object,  # Need any here to avoid circular dependancy issue
        "job_id": str,
        "symbol": str,
        "sentiment_limit": int,
        "ohlcv_limit": int
    }

    def __init__(
        self,
        context: dict[str, Any] = None,
        pipelines: dict[str, Pipeline] | list[Pipeline] = None,
        type_map: dict[str, Any] = None,
    ) -> None:
        if isinstance(type_map, dict):
            self.__type_map__ = type_map

        if isinstance(context, dict):
            self.__set_context__(context)
        else:
            self.__context__ = {}

        if isinstance(pipelines, list):
            self.__pipelines__ = self.__from_array__(pipelines)
        else:
            self.__pipelines__ = {}

        if isinstance(pipelines, dict):
            for pipe in pipelines.values():
                if not self.__is_valid_pipeline__(pipe):
                    return

            self.__pipelines__ = pipelines

    def __set_context__(self, context: dict[str, Any], **kwargs):
        if self.__context__ is None:
            self.__context__ = {}

        for key, value in self.__type_map__.items():
            if key not in context or context[key] is None:
                continue
            if isinstance(context[key], value):
                self.__context__[key] = context[key]

    def run_sequential(
        self,
        pipelines: dict[str, Pipeline] = None,
        context: dict[str, Any] = None,
    ) -> dict[str, Any]:
        if pipelines is not None and isinstance(pipelines, list):
            pipelines = self.__from_array__(pipelines)
        else:
            pipelines = self.__pipelines__

        if len(pipelines.values()) == 0:
            print(f"[{self}] No available pipelines.")
            return self.__context__

        if context is not None:
            self.__context__ = {**self.__context__, **context}

        print("Starting context \n", self.__context__)

        for pipe in pipelines.values():
            if self.__is_valid_pipeline__(pipe):
                pipe(self.__context__)
                if not self.__continue__():
                    break

        self.__reset_pipes__(pipelines)
        return self.__context__

    def run_threaded(
        self,
        pipelines: dict[str, Pipeline] = None,
        context: dict[str, Any] = None,
    ) -> dict[str, Any]:
        if pipelines is not None and isinstance(pipelines, list):
            pipelines = self.__from_array__(pipelines)
        else:
            pipelines = self.__pipelines__

        if len(pipelines.values()) == 0:
            print(f"[{self}] No available pipelines.")
            return self.__context__

        if context is not None:
            self.__context__ = {**self.__context__, **context}

        results = []
        for pipe in pipelines.values():
            if self.__is_valid_pipeline__(pipe):
                results.append(self.__thread__(pipe))

        self.__wait__(results)
        # print(f"Next Context \n", self.__context__)
        self.__reset_pipes__(pipelines)
        return self.__context__

    def insert_after(self, key: str, new_pipeline: Pipeline) -> "Engine":
        if not isinstance(new_pipeline, Pipeline):
            print(f"pipeline {new_pipeline} is not a valid pipeline")
            return
        if not isinstance(key, str):
            print(f"key is not a valid str {key}")
            return
        if key not in self.__pipelines__:
            print(f"key not in engine pipelines")
            return

        pipelines = {}
        for name, pipeline in self.__pipelines__.items():
            pipelines[name] = pipeline
            if name == key:
                print(
                    f"Inserting [pipeline={new_pipeline.__name__}] after [pipeline={name}]"
                )
                pipelines[new_pipeline.__name__] = new_pipeline

        self.__pipelines__ = pipelines
        return self

    def insert_before(self, key: str, new_pipeline: Pipeline) -> "Engine":
        if not isinstance(new_pipeline, Pipeline):
            print(f"pipeline {new_pipeline} is not a valid pipeline")
            return
        if not isinstance(key, str):
            print(f"key is not a valid str {key}")
            return
        if key not in self.__pipelines__:
            print(f"key not in engine pipelines")
            return

        pipelines = {}
        for name, pipeline in self.__pipelines__.items():
            if name == key:
                print(
                    f"Inserting [pipeline={new_pipeline.__name__}] before [pipeline={name}]"
                )
                pipelines[new_pipeline.__name__] = new_pipeline
            pipelines[name] = pipeline

        self.__pipelines__ = pipelines
        return self

    def __continue__(self):
        """Returns false to stop the engine.

        Returns:
            boolean: flag to stop engine
        """
        if "engine_stop" in self.__context__ and self.__context__["engine_stop"]:
            del self.__context__["engine_stop"]
            return False
        if (
            "engine_terminate" in self.__context__
            and self.__context__["engine_terminate"]
        ):
            self.__terminate_job__()
            del self.__context__
            return False

        return True

    def __terminate_job__(self):
        scheduler: BaseScheduler = self.__context__.get("scheduler")
        job_id: str = self.__context__.get("job_id")
        if isinstance(scheduler, BaseScheduler) and isinstance(job_id, str):
            print(f"[{self}] Terminating job", scheduler, job_id)
            scheduler.remove_job(job_id)

    def __reset_pipes__(self, pipelines: dict[str, Pipeline] = None):
        for pipe in pipelines.values():
            pipe.reset()

    def __wait__(self, results: list[Future]) -> dict[str, Any]:
        futures, _ = wait(results)
        for future in futures:
            try:
                result = future.result()
                print(f"Result of thread:", result)
                self.__context__ = {**self.__context__, **result}
            except Exception as e:
                print(f"Thread raised an exception: {e}")

    def __thread__(self, pipe: Pipeline) -> dict[str, Any]:
        t0 = time()
        try:
            if "threads" not in self.__context__:
                raise ValueError(
                    "Cannot run __thread__, ThreadPoolExecutor is missing from engine context"
                )
            threads: ThreadPoolExecutor = self.__context__["threads"]
            return threads.submit(pipe, {**self.__context__, "t0": t0})
        except Exception as e:
            print(f"Engine.__thread__ function raised an exception: {e}")

    def __from_array__(self, pipes: list[Pipeline]):
        """Requires Pipeline __name__ variable to be unique from other pipes or
        keys in __pipes dict will be overwritten.

        Args:
            pipes (list[Pipeline]): list of Pipelines for running jobs using the engine
        """
        pipelines = {}

        for pipe in pipes:
            if self.__is_valid_pipeline__(pipe):
                pipelines[pipe.__name__] = pipe

        return pipelines

    def __is_valid_pipeline__(self, pipe: Pipeline) -> bool:
        try:
            if not isinstance(pipe, Pipeline):
                raise TypeError(f"pipe object {pipe} is not a valid Pipeline")
            return True
        except TypeError as e:
            print(e)
            return False
