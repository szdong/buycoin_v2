from buyCoin import *


def lambda_handler(event, context):
    acct_info = AccountInfo(
        api_key="YOUR_API_KEY",
        api_secret="YOUR_API_KEY",
        # sub_account="YOUR_SUB_ACCOUNT",  # Default is None
        line_notify_key="YOUR_LINE_NOTIFY_API_KEY",
        initial_quote_balance=1000,
        initial_target_balance=0.2,
        order_size=10,
        digit=4  # ETH/USDT (Binance)
        # https://www.binance.com/en/trade-rule
    )
    # buy_coin = BuyCoin(account_info=acct_info, target_coin="ETH", quote_coin="USD", exchange=Exchange.binance)
    buy_coin = BuyCoin(account_info=acct_info, target_coin="ETH", quote_coin="USD", exchange=Exchange.ftx)
    buy_coin.execute()
