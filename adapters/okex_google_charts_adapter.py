from .adapter import Adapter


# Takes data from OKEX and adapts it to google-charts on client.
# Volume needs to be omitted client side for direct input into ChartJS.
class OkexGooleChartsAdapter(Adapter):

    def parse(self, data):
        response = []
        for ohlcv in data:

            response.append(
                [
                    # ts
                    int(ohlcv[0]) / 1000,
                    # low
                    float(ohlcv[3]),
                    # open
                    float(ohlcv[1]),
                    # close
                    float(ohlcv[4]),
                    # close
                    float(ohlcv[2]),
                ]
            )
        print(response)
        return response
