from flask import Flask, request
import requests
import os

app = Flask(__name__)

STOCKS_URL = "http://stocks:8000/stocks"
STOCK_VALUE_URL_TEMPLATE = "http://stocks:8000/stock-value/{stock_id}"


def get_current_price(stock_id):
    try:
        response = requests.get(STOCK_VALUE_URL_TEMPLATE.format(stock_id=stock_id))
        response.raise_for_status()
        return response.json().get("ticker", 0.0)
    except Exception as e:
        app.logger.error(f"Error fetching stock value for {stock_id}: {e}")
        return 0.0


@app.route('/capital-gains', methods=['GET'])
def capital_gains():
    query_params = request.args
    numsharesgt = query_params.get("numsharesgt", type=int)
    numshareslt = query_params.get("numshareslt", type=int)

    stocks = fetch_stocks(STOCKS_URL)

    if numsharesgt is not None:
        stocks = [s for s in stocks if s["shares"] > numsharesgt]
    if numshareslt is not None:
        stocks = [s for s in stocks if s["shares"] < numshareslt]

    total_gain = 0.0
    for stock in stocks:
        stock_value = get_current_price(stock["id"])
        capital_gain = (stock_value - stock["purchase price"]) * stock["shares"]
        total_gain += capital_gain

    return str(round(total_gain, 2)), 200


def fetch_stocks(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        app.logger.error(f"Error fetching stocks from {url}: {e}")
        return []


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5003))
    app.run(host='0.0.0.0', port=port)
