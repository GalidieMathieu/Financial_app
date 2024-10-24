# Project README

Issue with deployement, Change in "./docker_compose.yml" and "./financial_project/setting.py" <your_password> and <your_DataBaseName> so it can work locally with your PostGreDataBase.
launch two py script : 
- python manage.py makemigrations stocks
- python manage.py migrate 

## Overview
This project is a Django-based financial backtesting and reporting system. It includes several key functionalities such as fetching stock data, performing backtests, and generating detailed backtest reports in PDF format. All components run within a Docker environment managed by Docker Compose.

The following are the main entry points to interact with the application:
- `/fetch/<symbol>/`
- `/backtest/<symbol>/<initial_investment>/`
- `/generatebacktestreport/<symbol>/<initial_investment>/`

## Folder Structure
The project has a `docker-compose.yml` file, which is used to orchestrate the Docker containers required for the application, ensuring that all services are up and running seamlessly.

### Django URL Patterns
The following endpoints are defined in the Django application:

1. **Fetch Data Endpoint**
   - **URL:** `/fetch/<str:symbol>/`
   - **Function:** `fetch_data`
   - **Description:** This endpoint fetches stock data from an external API for the given symbol and saves it to the database.
   - **Example:** `/fetch/AAPL/` - This will fetch and store the stock data for Apple Inc. (AAPL).

2. **Backtest Strategy Endpoint**
   - **URL:** `/backtest/<str:symbol>/<int:initial_investment>/`
   - **Function:** `backtest_strategy`
   - **Description:** Executes a backtest on historical stock data for the given symbol and initial investment. The endpoint returns a JSON response with the computed total return, maximum drawdown, number of trades, and portfolio values over time.
   - **Example:** `/backtest/AAPL/5000/` - This will run a backtest on Apple Inc. with an initial investment of $5000.

3. **Generate Backtest Report Endpoint**
   - **URL:** `/generatebacktestreport/<str:symbol>/<int:initial_investment>/`
   - **Function:** `generate_backtest_report`
   - **Description:** Generates a PDF report summarizing the results of a backtest, including portfolio performance plots, stock data, and key metrics like total return and maximum drawdown.
   - **Example:** `/generatebacktestreport/AAPL/5000/` - This will generate a PDF report for the backtest performed on Apple Inc. with an initial investment of $5000.

## Data Model
The data is stored using the following model:

```python
class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.FloatField(default=0.0)
    high_price = models.FloatField(default=0.0)
    low_price = models.FloatField(default=0.0)
    close_price = models.FloatField(default=0.0)
    volume = models.BigIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp on creation
```

### Model Explanation
- **symbol**: The stock symbol (e.g., 'AAPL') for which data is recorded.
- **date**: The specific date for the stock data.
- **open_price**: Opening price of the stock on the specified date.
- **high_price**: Highest price of the stock during the day.
- **low_price**: Lowest price of the stock during the day.
- **close_price**: Closing price of the stock on the specified date.
- **volume**: Number of shares traded on the specified date.
- **timestamp**: Automatically captures the datetime when the record is created.

## Docker-Compose
The application is set up to run in Docker containers, making deployment and testing consistent and reliable. The `docker-compose.yml` file handles the configuration for setting up the Django application, the database, and any other required services.

## How to Run
To run this project locally using Docker, follow these steps:
1. Clone the repository.
2. Navigate to the project directory.
3. Run the following command to start the containers:
   ```bash
   docker-compose up --build
   ```
4. The application should now be running, and you can access the endpoints as described above.

## Endpoints Summary
- **`/fetch/<symbol>/`**: Fetches and stores stock data for the given symbol.
- **`/backtest/<symbol>/<initial_investment>/`**: Runs a backtest and returns a summary of results in JSON format.
- **`/generatebacktestreport/<symbol>/<initial_investment>/`**: Generates and returns a PDF report for the backtest.

## Notes
- The system uses a rate limit of 10 requests per minute per IP to avoid overwhelming the server or external data sources.
- The project utilizes Docker Compose to maintain consistency across different environments.

Feel free to modify the settings in `docker-compose.yml` or the Django settings files as per your deployment requirements.
