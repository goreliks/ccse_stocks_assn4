from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
import requests
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
import re

load_dotenv()

app = Flask(__name__)


MONGO_URI = 'mongodb://mongodb:27017/'
db_client = MongoClient(MONGO_URI)
db_name = os.getenv("DB_NAME", "stocks_db")
collection_name = os.getenv("COLLECTION_NAME", "stocks")
stocks_collection = db_client[db_name][collection_name]


def is_valid_date_format(date_str):
    if not date_str or date_str == 'NA':
        return True
    try:
        datetime.strptime(date_str, '%d-%m-%Y')
        return bool(re.match(r'^\d{2}-\d{2}-\d{4}$', date_str))
    except ValueError:
        return False


def validate_numeric_fields(data):
    try:
        price = float(data.get('purchase price', 0))
        shares = int(data.get('shares', 0))
        if price <= 0 or shares <= 0:
            return False
        return True
    except (ValueError, TypeError):
        return False


def get_stock_price(symbol):
    symbol = symbol.upper()
    api_key = os.getenv("NINJA_API_KEY")
    api_url = f'https://api.api-ninjas.com/v1/stockprice?ticker={symbol}'
    response = requests.get(api_url, headers={'X-Api-Key': api_key})

    if response.status_code == requests.codes.ok:
        data = response.json()
        if data and 'price' in data:
            return round(float(data['price']), 2)
        raise Exception("No price data available")
    else:
        raise Exception(f"API response code {str(response.status_code)}")


@app.route('/stocks', methods=['GET'])
def get_stocks():
    try:
        query_params = request.args
        query = {key: value for key, value in query_params.items()}

        stocks = list(stocks_collection.find(query, {"_id": 0}))
        return jsonify(stocks), 200
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route('/stocks', methods=['POST'])
def create_stock():
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({"error": "Expected application/json media type"}), 415

        data = request.get_json()

        required_fields = ['symbol', 'purchase price', 'shares']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Malformed data"}), 400

        if not validate_numeric_fields(data):
            return jsonify({"error": "Malformed data"}), 400

        purchase_date = data.get('purchase date')
        if purchase_date and not is_valid_date_format(purchase_date):
            return jsonify({"error": "Malformed data"}), 400

        symbol = data['symbol'].upper()

        stock = {
            'id': str(ObjectId()),
            'name': data.get('name', 'NA'),
            'symbol': symbol,
            'purchase price': round(float(data['purchase price']), 2),
            'purchase date': data.get('purchase date', 'NA'),
            'shares': int(data['shares'])
        }

        stocks_collection.insert_one(stock)
        return jsonify({'id': stock['id']}), 201

    except ValueError:
        return jsonify({"error": "Malformed data"}), 400
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route('/stocks/<string:stock_id>', methods=['GET'])
def get_stock(stock_id):
    try:
        stock = stocks_collection.find_one({"id": stock_id}, {"_id": 0})
        if not stock:
            return jsonify({"error": "Not found"}), 404
        return jsonify(stock), 200
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route('/stocks/<string:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    try:
        result = stocks_collection.delete_one({"id": stock_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Not found"}), 404
        return "", 204
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route('/stocks/<string:stock_id>', methods=['PUT'])
def update_stock(stock_id):
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({"error": "Expected application/json media type"}), 415

        data = request.get_json()
        required_fields = ['id', 'name', 'symbol', 'purchase price', 'purchase date', 'shares']

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Malformed data"}), 400

        if str(data['id']) != stock_id:
            return jsonify({"error": "Malformed data"}), 400

        if not validate_numeric_fields(data):
            return jsonify({"error": "Malformed data"}), 400

        if not is_valid_date_format(data['purchase date']):
            return jsonify({"error": "Malformed data"}), 400

        symbol = data['symbol'].upper()
        updated_stock = {
            'id': stock_id,
            'name': data['name'],
            'symbol': symbol,
            'purchase price': round(float(data['purchase price']), 2),
            'purchase date': data['purchase date'],
            'shares': int(data['shares'])
        }

        result = stocks_collection.replace_one({"id": stock_id}, updated_stock)
        if result.matched_count == 0:
            return jsonify({"error": "Not found"}), 404

        return jsonify({'id': stock_id}), 200

    except ValueError:
        return jsonify({"error": "Malformed data"}), 400
    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route('/stock-value/<string:stock_id>', methods=['GET'])
def get_stock_value(stock_id):
    try:
        stock = stocks_collection.find_one({"id": stock_id}, {"_id": 0})
        if not stock:
            return jsonify({"error": "Not found"}), 404

        current_price = get_stock_price(stock['symbol'])
        stock_value = round(current_price * stock['shares'], 2)

        return jsonify({
            'symbol': stock['symbol'],
            'ticker': current_price,
            'stock value': stock_value
        }), 200

    except Exception as e:
        return jsonify({"server error": str(e)}), 500


@app.route('/portfolio-value', methods=['GET'])
def get_portfolio_value():
    try:
        total_value = 0
        for stock in stocks_collection.find({}, {"_id": 0}):
            current_price = get_stock_price(stock['symbol'])
            total_value += current_price * stock['shares']

        return jsonify({
            'date': datetime.now().strftime('%d-%m-%Y'),
            'portfolio value': round(total_value, 2)
        }), 200

    except Exception as e:
        return jsonify({"server error": str(e)}), 500

@app.route('/kill', methods=['GET'])
def kill_container():
    os._exit(1)


if __name__ == '__main__':
    print("running portfolio server")
    app.run(host='0.0.0.0', port=5001, debug=True)

