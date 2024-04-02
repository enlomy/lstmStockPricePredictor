import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import schedule
# import time


def real_time_data_update():

    # Fetch stock data for Barclays PLC
    stock = yf.Ticker('BARC.L')

    today = datetime.today()
    yesterday = today - timedelta(days=1)

    # Get yesterday stock data
    data = stock.history(start=yesterday, end=today)

    file_path = "barc.csv"

    if data.empty:
        pass

    else:
        try:
            existing_data = pd.read_csv(file_path)
            existing_data['Date'] = pd.to_datetime(existing_data['Date'], utc=True)
            existing_data['Date'] = existing_data['Date'].dt.tz_localize(None).dt.date
            latest_date_in_csv = existing_data['Date'].max()
            
            # Filter new data that is greater than the latest date in CSV
            data.reset_index(inplace=True)  # Resetting index to use the 'Date' column
            data['Date'] = data['Date'].dt.date  # Ensuring 'Date' is in date format
            new_data = data[data['Date'] > latest_date_in_csv]
            
            if not new_data.empty:
                new_data = new_data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
                new_data.to_csv(file_path, mode='a', header=False, index=False)
                print("New data appended to the CSV.")
            else:
                print("No new data to append.")

        except FileNotFoundError:
            data.to_csv(file_path, mode='w', header=True, index=False)
            print("CSV file created with new data.")

# # real_time_data_update()
# schedule.every(1).seconds.do(real_time_data_update)
# schedule.every().day.at("04:00").do(real_time_data_update)


# # Start the scheduler
# while True:
#     schedule.run_pending()
#     time.sleep(3600)  # Sleep time