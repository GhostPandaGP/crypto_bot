import pandas as pd
import json
from bittrix import BittrexClient

NOTIFY_PAIR = ['USD-BTC', 'USD-LTC', 'USD-ETH']


def prepare_data(param):
    client = BittrexClient()
    for pair in param:
        current_price = client.get_ticker(pair=pair)

        res_frame = []
        for row in current_price['result']:
            res_frame.append(row)
            row['usd'] = pair

        usd = pd.DataFrame(res_frame)

        return usd

if __name__ == "__main__":
    prepare_data(NOTIFY_PAIR)
