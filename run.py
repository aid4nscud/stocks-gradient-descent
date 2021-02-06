import requests
import pandas as pd
import numpy as np
import json
import robin_stocks as r
from datetime import datetime
from sty import fg
import json
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def convert_list(list_input):

    data = json.dumps(list_input)
    parsed = json.loads(data)

    return parsed


def analyze_symbol(symbol):
    stock_data = r.stocks.get_stock_historicals(symbol, '5minute', 'day')

    close_prices = [float(i['close_price']) for i in stock_data]
    close_prices = np.array(close_prices)
    close_prices = close_prices.reshape(-1, 1)

    x = range(len(close_prices))
    x = np.array(x)
    x = x.reshape(-1, 1)

    line_fitter = LinearRegression()
    line_fitter.fit(x, close_prices)
    stock_predict = line_fitter.predict(x)

    plt.plot(x, close_prices)
    plt.plot(x, stock_predict)

    plt.show()


def get_curr_options():

    print("Current Options Trades: ")
    open_positions = r.get_open_option_positions()

    for option in open_positions:

        name = option['chain_symbol']

        num_contracts = float(option['quantity'])
        multiplier = num_contracts*100

        avg_price = float(option['average_price'])

        op_id = option['option_id']

        op_data = r.options.get_option_instrument_data_by_id(op_id)

        ed = datetime.strptime(op_data['expiration_date'], '%Y-%m-%d').date()

        td = datetime.today().strftime('%Y-%m-%d')
        td = datetime.strptime(td, '%Y-%m-%d').date()

        time_left = ed - td
        days_left = time_left.days

        op_type = op_data['type']

        strike_price = float((op_data['strike_price']))

        curr_option_data = r.options.get_option_market_data(
            name, op_data['expiration_date'], strike_price, op_type)

        curr_price = round(float(
            curr_option_data[0][0]['adjusted_mark_price']) * multiplier)

        profit = curr_price - avg_price

        print("Ticker: " + name)
        print("Average Cost: $" + str(avg_price))
        print("Current Price: $" + str(curr_price))
        if(profit < 0):
            print("Profit" + fg(255, 10, 10) + " $" + str(profit) + fg.rs)
        else:
            print("Profit:" + fg(0, 255, 0) + " $" + str(profit) + fg.rs)
        print("Time Until Expiration: " + str(days_left) + " Days")

        data = r.options.get_option_historicals(
            name, op_data['expiration_date'], op_data['strike_price'], op_type, '5minute', 'day')
        converted = convert_list(data)
        print(data)

        dataframe = pd.DataFrame(converted)

        close_prices = dataframe['close_price'].astype(float)

        x = range(close_prices.count())

        plt.plot(x, close_prices)

        plt.show()


def main():
    username = ''
    password = ''
    login = r.login(username, password)

    user_data = r.load_phoenix_account()
    portfolio_total = user_data['total_equity']['amount']
    total_dividends = r.get_total_dividends()

    print("Portfolio Value: " + str(portfolio_total) + fg.rs)
    print("Dividends Earned: " + str(total_dividends) + fg.rs)
    print("-")

    analyze_symbol('AAPL')


if __name__ == '__main__':
    main()
