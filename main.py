from buyCoin import *


def lambda_handler(event, context):
    acct_info = AccountInfo(
        api_key="YOUR_API_KEY",
        api_secret="YOUR_API_KEY",
        line_notify_key="YOUR_LINE_NOTIFY_API_KEY",
        initial_balance=1000,
        order_size=10,
        digit=4  # ETH/USDT (Binance)
        # https://www.binance.com/en/trade-rule
    )
    buy_coin = BuyCoin(account_info=acct_info, target_coin="ETH", quote_coin="USDT")
    buy_coin.execute()