import pandas as pd
import json
from bittrix import BittrexClient

NOTIFY_PAIR = ['USD-BTC', 'USD-LTC', 'USD-ETH']


def prepare_data(param):
    client = BittrexClient()
    res_frame = []
    for pair in param:

        print(pair)
        current_price = client.get_ticker(pair=pair)

        for row in current_price['result']:
            res_frame.append(row)
            row['usd'] = pair

    usd = pd.DataFrame(res_frame)
    usd.to_csv('usd.csv', sep=';')

    return usd


if __name__ == "__main__":
    prepare_data(NOTIFY_PAIR)
