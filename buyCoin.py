import requests
import traceback
import ccxt
import json
import time


class Exchange:
    binance = "Binance"
    ftx = "FTX"


class AccountInfo:
    def __init__(self, api_key: str, api_secret: str, line_notify_key: str, initial_balance: float, order_size: float,
                 digit: int, sub_account: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.sub_account = sub_account
        self.line_notify_key = line_notify_key

        # Total amount invested to date (USD or USDT or USDC).
        self.initial_balance = initial_balance

        # Amount of money you want to invest every day from next day (USD or USDT or USDC).
        self.order_size = order_size

        # Minimum Order Quantity Precision (ex: 0.000001: 6, 0.001: 3)
        self.digit = digit


class BuyCoin:
    def __init__(self, account_info: AccountInfo, target_coin: str, quote_coin: str, exchange: str):
        if exchange == "Binance":
            self.exchange = ccxt.binance({
                'apiKey': account_info.api_key,
                'secret': account_info.api_secret,
            })
        elif exchange == "FTX":
            ccxt_info = {
                'apiKey': account_info.api_key,
                'secret': account_info.api_secret,
            }
            if account_info.sub_account is not None:
                ccxt_info["headers"] = {
                    'FTX-SUBACCOUNT': account_info.sub_account,
                }
            self.exchange = ccxt.ftx(ccxt_info)
        else:
            raise ValueError("Unsupported exchange. Please use Binance or FTX.")

        self.account_info = account_info
        self.symbol = f"{target_coin}/{quote_coin}"
        self.target_coin = target_coin
        self.quote_coin = quote_coin

    def execute(self):
        coin_price = float(self.exchange.fetch_ticker(symbol=self.symbol)["last"])
        order_amount = round(self.account_info.order_size / coin_price, self.account_info.digit)
        order_amount += 2 / 10 ** min(6, self.account_info.digit)
        print(f"Order Size: {order_amount}")

        check = False
        while not check:
            try:
                market_buy_order = self.exchange.create_market_buy_order(
                    symbol=self.symbol,
                    amount=order_amount
                )
                self.line_notify(message=str(json.dumps(market_buy_order["info"], indent=4)))
                check = True
            except Exception as e:
                error_msg = f"{e}\n"
                error_msg += traceback.format_exc()
                self.line_notify(error_msg)
                check = False
                time.sleep(10)

        if check:
            quote_balance = self.exchange.fetch_balance()[self.quote_coin]["free"]
            coin_balance = self.exchange.fetch_balance()[self.target_coin]["free"]
            print(json.dumps(self.exchange.fetch_balance(), indent=4))

            avg_cost = round((self.account_info.initial_balance - quote_balance) / coin_balance, 3)
            roe = (quote_balance + coin_balance * coin_price - self.account_info.initial_balance) * 100
            roe /= (self.account_info.initial_balance - quote_balance)
            Estimated_Value = quote_balance + coin_balance * coin_price

            text = f"{self.symbol}: {coin_price}\n\n"
            text += f"[Balance] \n"
            text += f"{self.quote_coin}: {round(quote_balance, 2)}\n"
            text += f"{self.target_coin}: {round(coin_balance, self.account_info.digit)}\n"
            text += f"Avg: {avg_cost}\n\n"
            text += f"Estimated Value: {round(Estimated_Value, 3)}\n"
            text += f"ROE: {round(roe, 3)}%"

            self.line_notify(message=text)
        else:
            error_msg = "Something Error"
            self.line_notify(message=error_msg)
            raise ValueError(error_msg)

    def line_notify(self, message: str, pic: bool = False, path: str = None):
        line_api_end_point = 'https://notify-api.line.me/api/notify'
        message = "\n" + message
        payload = {'message': message}

        if not pic:
            headers = {'Authorization': 'Bearer ' + self.account_info.line_notify_key}
            requests.post(line_api_end_point, data=payload, headers=headers)
        else:
            files = {"imageFile": open(path, "rb")}
            headers = {'Authorization': 'Bearer ' + self.account_info.line_notify_key}
            requests.post(line_api_end_point, data=payload, headers=headers, files=files)
