# import pytest
# import requests

# # Base URLs for services
# CAPITAL_GAINS_URL = "http://localhost:5003"
# STOCKS_URL = "http://localhost:5001"

# # Sample stocks for testing
# stock1 = {
#     "name": "NVIDIA Corporation",
#     "symbol": "NVDA",
#     "purchase price": 134.66,
#     "purchase date": "18-06-2024",
#     "shares": 7
# }

# stock2 = {
#     "name": "Apple Inc.",
#     "symbol": "AAPL",
#     "purchase price": 183.63,
#     "purchase date": "22-02-2024",
#     "shares": 19
# }

# stock3 = {
#     "name": "Alphabet Inc.",
#     "symbol": "GOOG",
#     "purchase price": 140.12,
#     "purchase date": "24-10-2024",
#     "shares": 14
# }

# stock4 = {
#     "name": "Tesla, Inc.",
#     "symbol": "TSLA",
#     "purchase price": 194.58,
#     "purchase date": "28-11-2022",
#     "shares": 32
# }

# stock5 = {
#     "name": "Microsoft Corporation",
#     "symbol": "MSFT",
#     "purchase price": 420.55,
#     "purchase date": "09-02-2024",
#     "shares": 35
# }

# stock6 = {
#     "name": "Intel Corporation",
#     "symbol": "INTC",
#     "purchase price": 19.15,
#     "purchase date": "13-01-2025",
#     "shares": 10
# }

# stock7 = {
#     "name": "Amazon.com, Inc.",
#     "purchase price": 134.66,
#     "purchase date": "18-06-2024",
#     "shares": 7
# }

# stock8 = {
#     "name": "Amazon.com, Inc.",
#     "symbol": "AMZN",
#     "purchase price": 134.66,
#     "purchase date": "Tuesday, June 18, 2024",
#     "shares": 7
# }

# meta_data = {}

# @pytest.fixture
# def stocks_url():
#     return STOCKS_URL


# @pytest.fixture
# def capital_gains_url():
#     return CAPITAL_GAINS_URL


# def test_post_stocks(stocks_url):
#     ids = []
#     for stock, stock_meta in zip([stock1, stock2, stock3], ['stock1', 'stock2', 'stock3']):
#         response = requests.post(f"{stocks_url}/stocks", json=stock)
#         assert response.status_code == 201
#         response_data = response.json()
#         assert "id" in response_data
#         ids.append(response_data["id"])
#         meta_data[stock_meta] = {"id": response_data["id"]}
#     assert len(ids) == len(set(ids))


# def test_get_stock(stocks_url):
#     stock_1_id = meta_data['stock1']['id']

#     response = requests.get(f"{stocks_url}/stocks/{stock_1_id}")
#     assert response.status_code == 200
#     response_data = response.json()
#     assert response_data["symbol"] == "NVDA"


# def test_get_all_stocks(stocks_url):
#     response = requests.get(f"{stocks_url}/stocks")
#     assert response.status_code == 200
#     response_data = response.json()
#     assert len(response_data) == 3


# def test_get_stock_value(stocks_url):
#     for stock, expected_symbol in zip([meta_data['stock1'],
#                                           meta_data['stock2'],
#                                           meta_data['stock3']],
#                                          ["NVDA", "AAPL", "GOOG"]):

#         response = requests.get(f"{stocks_url}/stock-value/{stock['id']}")
#         assert response.status_code == 200
#         response_data = response.json()
#         assert response_data["symbol"] == expected_symbol
#         stock['sv'] = response_data["stock value"]


# def test_portfolio_value(stocks_url):
#     response = requests.get(f"{stocks_url}/portfolio-value")
#     assert response.status_code == 200
#     response_data = response.json()
#     portfolio_value = response_data["portfolio value"]

#     sv1 = meta_data['stock1']['sv']
#     sv2 = meta_data['stock2']['sv']
#     sv3 = meta_data['stock3']['sv']
#     total_value = sv1 + sv2 + sv3

#     assert portfolio_value * 0.97 <= total_value <= portfolio_value * 1.03


# def test_invalid_stock_symbol(stocks_url):
#     response = requests.post(f"{stocks_url}/stocks", json=stock7)
#     assert response.status_code == 400


# def test_delete_stock(stocks_url):
#     stock_id = meta_data['stock2']['id']

#     response = requests.delete(f"{stocks_url}/stocks/{stock_id}")
#     assert response.status_code == 204


# def test_get_deleted_stock(stocks_url):
#     stock_id = meta_data['stock2']['id']

#     response = requests.get(f"{stocks_url}/stocks/{stock_id}")
#     assert response.status_code == 404


# def test_invalid_purchase_date(stocks_url):
#     response = requests.post(f"{stocks_url}/stocks", json=stock8)
#     assert response.status_code == 400
import requests
import pytest

BASE_URL = "http://localhost:5001" 

# Stock data
stock1 = { "name": "NVIDIA Corporation", "symbol": "NVDA", "purchase price": 134.66, "purchase date": "18-06-2024", "shares": 7 }
stock2 = { "name": "Apple Inc.", "symbol": "AAPL", "purchase price": 183.63, "purchase date": "22-02-2024", "shares": 19 }
stock3 = { "name": "Alphabet Inc.", "symbol": "GOOG", "purchase price": 140.12, "purchase date": "24-10-2024", "shares": 14 }

def test_post_stocks():
    response1 = requests.post(f"{BASE_URL}/stocks", json=stock1)
    response2 = requests.post(f"{BASE_URL}/stocks", json=stock2)
    response3 = requests.post(f"{BASE_URL}/stocks", json=stock3)
    
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response3.status_code == 201

    # Ensure unique IDs
    data1 = response1.json()
    data2 = response2.json()
    data3 = response3.json()
    assert data1['id'] != data2['id']
    assert data1['id'] != data3['id']
    assert data2['id'] != data3['id']

def test_get_stocks():
    response = requests.get(f"{BASE_URL}/stocks")
    assert response.status_code == 200
    stocks = response.json()
    assert len(stocks) == 3 
    
def test_get_portfolio_value():
    response = requests.get(f"{BASE_URL}/portfolio-value")
    assert response.status_code == 200
    portfolio_value = response.json()
    assert portfolio_value['portfolio value'] > 0  # Portfolio value should be greater than 0

def test_post_stocks_invalid_data():
    stock_invalid = { "name": "Amazon", "purchase price": 100.50, "purchase date": "15-03-2025", "shares": 50 }
    response = requests.post(f"{BASE_URL}/stocks", json=stock_invalid)
    assert response.status_code == 400


