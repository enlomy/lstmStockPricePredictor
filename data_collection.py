import yfinance as yf
from datetime import datetime, timedelta

def get_stock_data(symbol):

    # Fetch stock data for Barclays PLC
    stock = yf.Ticker(symbol)
    
    today = datetime.today()
    startdate = today - timedelta(days=5500)
    yesterday = today - timedelta(days=1)

    # Get historical market data for Barclays PLC
    data = stock.history(start=startdate, end=yesterday)
    
    # Extract relevant information: Open, High, Low, Close, Volume
    stock_data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    return stock_data

if __name__ == "__main__":

    # Symbol for Barclays PLC stock
    symbol = 'BARC.L'
    
    # Get Barclays PLC stock data
    nvidia_data = get_stock_data(symbol)

    # csv_filename = 'barc.csv'
    csv_filename = 'barc.csv'
    nvidia_data.to_csv(csv_filename)