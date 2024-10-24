from .models import StockData
from datetime import datetime, timedelta

def reset_dataBase_with_new_data (data , symbol) :
    """
    Resets the StockData table with new data provided.

    Inputs:
    - data: Dictionary containing the time series stock data, with dates as keys and daily data (open, high, low, close, volume) as values.
    - symbol: The stock symbol for which the data is being reset.

    Outputs:
    - Returns a dictionary of filtered data for JSON response, containing dates and corresponding daily stock data.

    This function clears all records from the StockData table, then inserts new records for the given symbol.
    Only data from the last two years is inserted. The function also handles any database errors that might occur during the insertion process.
    """
    # Clear all records from the StockData table
    StockData.objects.all().delete()

    # Define the cutoff date for 2 years ago
    cutoff_date = datetime.now() - timedelta(days=730)  # Approximately 2 years
    #for debug
    filtered_data = {}

    for date, daily_data in data.items():

        # Convert the date string to a datetime object
        date_obj = datetime.strptime(date, '%Y-%m-%d')

        # Check if the date is less than the cutoff date
        if date_obj < cutoff_date:
            break  # Stop the loop if the date is more than 2 years old

        try:
            StockData.objects.get_or_create(
                symbol=symbol,
                date=date,
                defaults={
                    'open_price': daily_data['1. open'],
                    'high_price': daily_data['2. high'],
                    'low_price': daily_data['3. low'],
                    'close_price': daily_data['4. close'],
                    'volume': daily_data['5. volume'],
                },
            )
            # Store filtered data for JSON response
            filtered_data[date] = {
                'open_price': daily_data['1. open'],
                'high_price': daily_data['2. high'],
                'low_price': daily_data['3. low'],
                'close_price': daily_data['4. close'],
                'volume': daily_data['5. volume'],
            }
        except Exception as db_err:
            print(f"Database error occurred while processing date {date}: {db_err}")
            continue
    
    return filtered_data

def compute_backtest(symbol='AAPL', initial_investment=1000):
    """
    Computes the backtest for a given stock symbol using historical data and a basic moving average strategy.

    Inputs:
    - symbol: The stock symbol for which the backtest is executed (default: 'AAPL').
    - initial_investment: The initial amount of money to invest in the backtest (default: 1000).

    Outputs:
    - Returns a dictionary containing:
      - 'compute_data': A dictionary with the total return, maximum drawdown, total number of trades, and portfolio values over time.
      - 'stock_data': A list of dictionaries containing the stock's date and closing price.

    The function uses a moving average strategy to make buy and sell decisions:
    - Buy when the stock price falls below the 50-day moving average.
    - Sell when the stock price rises above the 200-day moving average.
    """
    data = StockData.objects.filter(symbol=symbol).order_by('date')
    # Exception handling for empty or None data
    if data is None or not data.exists():
        return {
            'error': 'No data available for the specified symbol.'
        }

    portfolio_values = []
    # Parameters for moving averages
    moving_average_short = 50  # 50-day moving average
    moving_average_long = 200  # 200-day moving average

    ma50_total, ma200_total = 0, 0
    cash = initial_investment
    stock_owned, buy_price, peak_value, total_trades, MaxDrawdown = 0, 0, 0, 0, 0

    stock_data = []

    for i, day in enumerate(data):
        stock_data.append({
            'date': day.date.strftime('%Y-%m-%d'),
            'close_price': day.close_price
        })

        ma50_value, ma200_value = 0, 0

        # Calculating close_price for the last 200 and 50 days
        if i < 49:
            ma50_total += day.close_price
            ma50_value = ma50_total / (i + 1)
            ma200_total += day.close_price
            ma200_value = ma200_total / (i + 1)
        elif 49 <= i < 199:
            ma50_total += day.close_price
            ma50_total -= data[i - 49].close_price
            ma50_value = ma50_total / 50
            ma200_total += day.close_price
            ma200_value = ma200_total / (i + 1)
        elif i >= 199:
            ma50_total += day.close_price
            ma50_total -= data[i - 49].close_price
            ma50_value = ma50_total / 50
            ma200_total += day.close_price
            ma200_total -= data[i - 199].close_price
            ma200_value = ma200_total / 200

        # Buy condition
        if cash != 0 and day.close_price < ma50_value:
            stock_owned = cash / day.close_price
            cash = 0
            buy_price = day.close_price
            total_trades += 1

        # Sell condition
        elif stock_owned > 0 and day.close_price > ma200_value:
            cash = stock_owned * day.close_price
            stock_owned = 0
            total_trades += 1

        total_CurrentValue = cash + (stock_owned * data.last().close_price if stock_owned > 0 else 0)
        portfolio_values.append(total_CurrentValue)

        # Data for drawdown
        if total_CurrentValue > peak_value:
            peak_value = total_CurrentValue
        else:
            currentDrawdown = (peak_value - total_CurrentValue) / peak_value
            MaxDrawdown = max(MaxDrawdown, currentDrawdown)

    total_return = ((cash + (stock_owned * data.last().close_price if stock_owned > 0 else 0) - initial_investment) / initial_investment) * 100

    return {
        'compute_data': {
            'total_return': total_return,
            'Max_Drawdown': MaxDrawdown,
            'total_trades': total_trades,
            'portfolio_values': portfolio_values,
        },
        'stock_data': stock_data
    }
