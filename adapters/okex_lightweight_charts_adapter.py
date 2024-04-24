from typing import Any
from .adapter import Adapter
from datetime import datetime


# Takes data from OKEX and adapts it to lightweight-charts (tradingview) on client.
# Volume needs to be omitted client side for direct input into ChartJS.
class OkexLightweightChartsAdapter(Adapter):

    # HELP
    # If you can write a function that converts a x-xxxx-xxxx-xxxx sized utc timestamp to:
    # https://tradingview.github.io/lightweight-charts/docs/time-zones#note-about-converting-to-a-local-time-zone
    # https://tradingview.github.io/lightweight-charts/docs/time-zones#date-solution
    def __to_local(self, date: str):
        d = datetime.utcfromtimestamp(int(date) / 1000)

        # Convert to local datetime
        local_datetime = d.replace(tzinfo=None)  # Assuming the original time is in UTC

        # Convert local datetime to seconds since the Unix Epoch
        local_timestamp = int(local_datetime.timestamp())

        return local_timestamp

    def parse(self, data: Any) -> dict[str, Any]:
        return {
            "time": int(data[0]) / 1000,
            "open": float(data[1]),
            "high": float(data[2]),
            "low": float(data[3]),
            "close": float(data[4]),
        }

    def parse_list(self, data: list) -> list:
        response = list()
        for ohlcv in data:
            response.append(self.parse(ohlcv))
        response.reverse()
        return response
