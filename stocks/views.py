import requests
from django.conf import settings
from .controller import *
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from matplotlib import pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle , tableofcontents
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import json
from reportlab.lib.utils import ImageReader



#@ratelimit(key='ip', rate='10/m', method='ALL', block=True)  # Limit to 10 requests per minute per IP
def fetch_data(request , symbol):
    """
    Parameters:
        request (HttpRequest): The HTTP request object containing query parameters.
        symbol (str): The stock symbol for which to fetch data. Defaults to 'AAPL' 
                      if not provided in the request.

    Returns:
        JsonResponse: A JSON response containing the fetched stock data, including
                      open, high, low, close prices, and volume, for the last 
                      two years.

    Process:
        1. Retrieve the stock symbol from the request's query parameters, defaulting 
           to 'AAPL' if not provided.
        2. Construct the API request URL using the specified stock symbol and API key.
        3. Send a GET request to the Alpha Vantage API to retrieve daily stock data.
        4. Clear all existing records in the StockData table to ensure fresh data.
        5. Calculate the cutoff date to filter out data older than two years.
        6. Iterate over the retrieved daily stock data, storing only data within the 
           last two years in the StockData table.
        7. Prepare a filtered dataset for the JSON response, including only the relevant
           fields for each date.

    Note:
        - Ensure the StockData model is correctly defined and accessible for 
          data storage.
        - The Alpha Vantage API has usage limits; consider implementing error handling
          for exceeded limits or connection issues.
    """

    try:
        print("start of fetch_data")
        base_url = settings.ALPHA_VANTAGE_BASE_URL
        function = settings.ALPHA_VANTAGE_FUNCTION
        requested_symbol = request.GET.get('symbol') or symbol or 'AAPL'
        api_key = settings.ALPHA_VANTAGE_API_KEY
        outputSize = settings.ALPHA_VANTAGE_OUTPUTSIZE

        #url = f'{base_url}?function={function}&symbol={requested_symbol}&apikey={api_key}&outputsize={outputSize}'
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=PENHU30WNPYGZVWH&outputsize=full'
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json().get('Time Series (Daily)', {})

         # Check if the response data is None
        if data is None:
            return JsonResponse({'error': 'Received null response from API.'}, status=502)  # Bad Gateway

         # Check if data.items() is empty
        if not data:
            return JsonResponse({'error': 'No time series data available for the given symbol.'}, status=404)

        # Call the reset function
        filtered_data = reset_dataBase_with_new_data(data, symbol)
        
        return JsonResponse(filtered_data, safe=False)

    except requests.exceptions.HTTPError as http_err:
        return JsonResponse({'error': f'HTTP error occurred: {http_err}'}, status=500)
    except requests.exceptions.RequestException as req_err:
        return JsonResponse({'error': f'Request error occurred: {req_err}'}, status=500)
    except Exception as err:
        return JsonResponse({'error': f'An error occurred: {err}'}, status=500)


# Existing backtest code from the user
#@ratelimit(key='ip', rate='10/m', method='ALL', block=True)  # Limit to 10 requests per minute per IP
def backtest_strategy(request, symbol='AAPL', initial_investment=1000):
    """
    Executes a backtest for the specified stock symbol and returns the result.

    Inputs:
    - request: Django HTTP request object, used to track and rate-limit requests.
    - symbol: The stock symbol for which the backtest is executed (default: 'AAPL').
    - initial_investment: The initial amount of money to invest in the backtest (default: 1000).

    Outputs:
    - Returns a JsonResponse containing the backtest result, which includes:
      - Total return.
      - Maximum drawdown.
      - Total number of trades.
      - Portfolio values over time.

    The function calls the compute_backtest function to perform the backtest and then formats the result as a JSON response.
    """
    try:
        backtest_result = compute_backtest(symbol, initial_investment)
        if 'error' in backtest_result:
            return JsonResponse({'error': backtest_result['error']}, status=404)
        return JsonResponse(backtest_result)

    except Exception as err:
        return JsonResponse({'error': f'An error occurred during backtesting: {err}'}, status=500)




#@ratelimit(key='ip', rate='10/m', method='ALL', block=True)  # Limit to 10 requests per minute per IP
#@csrf_exempt
def generate_backtest_report(request, symbol='AAPL', initial_investment=1000):
    """
    Generates a backtest report as a PDF document.

    Parameters:
    - request: Django HTTP request object, containing information about the request.
    - symbol: The stock symbol for which the backtest report is generated (default: 'AAPL').
    - initial_investment: The initial amount of money to invest in the backtest (default: 1000).

    Returns:
    - Returns an HTTP response with a PDF attachment containing the backtest report, including:
      - Portfolio performance plot.
      - Stock data plot.
      - Summary table of metrics (total return, max drawdown, total trades).
      - Evaluation summary.

    The function first runs a backtest using the specified symbol and initial investment, parses the
    backtest results, generates relevant plots, and compiles all of these into a PDF document.
    """
    try:
        # Run backtest
        response = backtest_strategy(request, symbol, initial_investment)
        if response.status_code != 200:
            return response

        try:
            # Parse response JSON
            backtest_result = json.loads(response.content)
            portfolio_values = backtest_result.get('compute_data', {}).get('portfolio_values', [])
            total_return = backtest_result.get('compute_data', {}).get('total_return')
            max_drawdown = backtest_result.get('compute_data', {}).get('Max_Drawdown')
            total_trades = backtest_result.get('compute_data', {}).get('total_trades')
            stock_data = backtest_result.get('stock_data', [])
        except Exception as err:
            return JsonResponse({'error': f'Error parsing backtest response data: {err}'}, status=500)

        try:
            # Generate performance plot for portfolio value
            plt.figure()
            plt.plot(portfolio_values, label='Portfolio Value')
            plt.xlabel('Time')
            plt.ylabel('Portfolio Value ($)')
            plt.title(f'Backtest Performance for {symbol}')
            plt.legend()
            plt.tight_layout()
            stock_buf = BytesIO()
            plt.savefig(stock_buf, format='png')
            stock_buf.seek(0)
            plt.close()  # Close the plot to free memory
        except Exception as err:
            return JsonResponse({'error': f'Error generating portfolio value plot: {err}'}, status=500)

        try:
            # Generate stock data plot with reduced x-axis labels
            plt.figure()
            stock_dates = [entry['date'] for entry in stock_data]
            stock_prices = [entry['close_price'] for entry in stock_data]
            plt.plot(stock_dates, stock_prices, label='Stock Price')
            plt.xlabel('Date')
            plt.ylabel('Stock Price ($)')
            plt.title(f'Stock Data for {symbol}')
            plt.legend()
            plt.xticks(ticks=range(0, len(stock_dates), max(1, len(stock_dates) // 20)), rotation=45)  # Show fewer date labels
            plt.tight_layout()
            plt_buf = BytesIO()
            plt.savefig(plt_buf, format='png')
            plt_buf.seek(0)
            plt.close()  # Close the plot to free memory
        except Exception as err:
            return JsonResponse({'error': f'Error generating stock data plot: {err}'}, status=500)

        # Generate PDF
        pdf_buf = BytesIO()
        pdf_canvas = canvas.Canvas(pdf_buf, pagesize=letter)

        # Draw portfolio value plot
        try:
            portfolio_image = ImageReader(plt_buf)
            pdf_canvas.drawImage(portfolio_image, 50, 500, width=500, height=200)
        except Exception as err:
            return JsonResponse({'error': f'Error adding portfolio value plot to PDF: {err}'}, status=500)

        # Draw stock data plot
        try:
            pdf_canvas.drawString(50, 220, f'Stock Data for {symbol}')
            stock_image = ImageReader(stock_buf)
            pdf_canvas.drawImage(stock_image, 50, 250, width=500, height=200)
            
        except Exception as err:
            return JsonResponse({'error': f'Error adding stock data plot to PDF: {err}'}, status=500)

        # Draw table of metrics
        try:
            data = [['Metric', 'Value'],
                    ['Total Return', f'{total_return:.2f}%'],
                    ['Max Drawdown', f'{max_drawdown*100:.2f}%'],
                    ['Total Trades', total_trades]]
            table = Table(data, colWidths=[200, 200])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            table.wrapOn(pdf_canvas, 50, 200)
            table.drawOn(pdf_canvas, 50, 100)
        except Exception as err:
            return JsonResponse({'error': f'Error adding metrics table to PDF: {err}'}, status=500)


        # Finalize PDF
        pdf_canvas.save()
        pdf_buf.seek(0)

        # Return PDF as downloadable file
        response = HttpResponse(pdf_buf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{symbol}_backtest_report.pdf"'
        return response

    except Exception as err:
        return JsonResponse({'error': f'An unexpected error occurred during report generation: {err}'}, status=500)



#Obsolate has we can use backtest_strategy
#@csrf_exempt
def generate_json_report(request, symbol='AAPL', initial_investment=1000):
    try:
        # Run backtest
        response = backtest_strategy(request, symbol, initial_investment)
        if response.status_code != 200:
            return response

        backtest_result = json.loads(response.content)
        return JsonResponse(backtest_result, status=200)

    except Exception as err:
        return JsonResponse({'error': f'An error occurred during report generation: {err}'}, status=500)