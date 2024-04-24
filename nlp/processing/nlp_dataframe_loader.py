import pandas as pd


class NLPDataFrameLoader:
    def __init__(self, **kwargs) -> None:
        base_dir = kwargs.get("base_dir", "./data/")
        filename = kwargs.get("filename", "stock_data")
        temp_file = kwargs.get("temp_file", None)
        encoding = kwargs.get("encoding", "utf-8")

        try:
            if not isinstance(base_dir, str):
                raise TypeError()
            if not isinstance(filename, str):
                raise TypeError()
            if not isinstance(encoding, str):
                raise TypeError()
            if temp_file is not None and not isinstance(temp_file, str):
                raise TypeError()

            self.base_dir = base_dir
            self.filename = filename
            self.temp_file = temp_file
            self.encoding = encoding

        except TypeError as e:
            print(e)

    def read(self, **kwargs):
        filename = kwargs.get("filename", self.filename)
        temp_file = kwargs.get("temp_file", self.temp_file)
        base_dir = kwargs.get("base_dir", self.base_dir)
        encoding = kwargs.get("encoding", self.encoding)
        encoding_error_handler = kwargs.get("encoding_errors", "replace")
        names = kwargs.get("names", None)

        try:
            if not isinstance(base_dir, str):
                raise TypeError(
                    "[NLPDataFrameLoader(error = base_dir argument is not a str)]"
                )

            if temp_file is not None and isinstance(temp_file, str):
                print(
                    f"[NLPDataFrameLoader(read = Reading from {base_dir}temp/{temp_file})]"
                )
                return pd.read_csv(
                    f"{base_dir}temp/{temp_file}",
                    compression="gzip",
                    encoding=encoding,
                    encoding_errors=encoding_error_handler,
                    names=names,
                )

            print(f"[NLPDataFrameLoader(read = Reading from {base_dir}{filename})]")
            return pd.read_csv(
                f"{base_dir}{filename}",
                encoding=encoding,
                encoding_errors=encoding_error_handler,
                names=names,
            )

        except TypeError as e:
            print(e)
