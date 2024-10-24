import numpy as np
import pandas as pd
import pickle
import requests
import os
from django.http import JsonResponse
from django.conf import settings

def predict_stock_prices(symbol):
    try:
        # Build the API URL
        base_url = settings.ALPHA_VANTAGE_BASE_URL
        function = settings.ALPHA_VANTAGE_FUNCTION
        api_key = settings.ALPHA_VANTAGE_API_KEY
        output_size = settings.ALPHA_VANTAGE_OUTPUTSIZE

        url = f'{base_url}?function={function}&symbol={symbol}&apikey={api_key}&outputsize={output_size}'
        
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Fetch the time series data
        data = response.json().get('Time Series (Daily)', {})

        # Check if data is empty
        if not data:
            return JsonResponse({'error': 'No time series data available for the given symbol.'}, status=404)

        # Create a DataFrame from the fetched data
        df = pd.DataFrame.from_dict(data, orient='index')

        # Rename the columns to remove the prefixes
        df.rename(columns={
            '1. open': 'open_price',
            '2. high': 'high_price',
            '3. low': 'low_price',
            '4. close': 'close_price',
            '5. volume': 'volume'
        }, inplace=True)

        # Reset the index to use 'date' as a column
        df.index.name = 'date'
        df.reset_index(inplace=True)

        # Convert columns to appropriate data types
        df['open_price'] = df['open_price'].astype(float)
        df['high_price'] = df['high_price'].astype(float)
        df['low_price'] = df['low_price'].astype(float)
        df['close_price'] = df['close_price'].astype(float)
        df['volume'] = df['volume'].astype(float)

        # Ensure the 'date' column is in datetime format
        df['date'] = pd.to_datetime(df['date'])

        # Sort the DataFrame by date
        df = df.sort_values('date')

        # Select only the 'date' and 'close_price' columns
        filtered_df = df[['date', 'close_price']]
        
        # Get the last 30 rows
        last_30_rows_df = filtered_df.tail(30)

        # Reshape the close prices for future predictions
        future_X = last_30_rows_df['close_price'].values.reshape(-1, 1)

        # Load the model
        model_file_path = os.path.join(os.path.dirname(__file__), 'ML_model', 'linear_regression_model.pkl')
        
        try:
            with open(model_file_path, 'rb') as file:
                loaded_model = pickle.load(file)
        except FileNotFoundError:
            raise FileNotFoundError("Model file not found.")
        except pickle.UnpicklingError:
            raise ValueError("Error unpickling the model file.")

        # Make predictions
        future_predictions = loaded_model.predict(future_X)

        return future_predictions  # Return the predictions here

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
