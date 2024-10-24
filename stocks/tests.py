from django.test import TestCase
from .models import StockData
from .views import backtest_strategy  # Ensure you have the correct import path
from django.urls import reverse
from django.http import JsonResponse
import os
import json

class BacktestStrategyTests(TestCase):
    
    def setUp(self):

        # Clear any existing StockData
        StockData.objects.all().delete()  # Ensure a clean state for each test
        # Set up initial data for the tests

        # Construct the absolute path to the JSON file
        json_file_path = os.path.join(os.path.dirname(__file__), 'stockTestData', 'stock_data.json')


        with open(json_file_path, 'r') as file:
            json_data = json.load(file)

        # Populate the database with data from the JSON file
        for date, values in json_data.items():
            StockData.objects.create(
                symbol='AAPL',
                date=date,
                open_price=values['open_price'],
                high_price=values['high_price'],
                low_price=values['low_price'],
                close_price=values['close_price'],
                volume=values['volume']
            )
        
    def test_valid_backtest(self):
        response = self.client.get(reverse('backtest_strategy', kwargs={'symbol': 'AAPL' , 'initial_investment': 5000}))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        #Testing if dataHas been correctly done
        tolerance = 1e-3  # 0.001 for 1/1000
        self.assertAlmostEqual(3.0685891202704516, data['total_return'] , delta=tolerance)
        self.assertAlmostEqual(0.4327953812967894, data['Max_Drawdown'])
        self.assertEqual(74, data['total_trades'])

    def test_no_data(self):
        # Clear the data
        StockData.objects.all().delete()
        
        response = self.client.get(reverse('backtest_strategy', kwargs={'symbol': 'AAPL', 'initial_investment': 5000}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'No data available for the specified symbol.'})
        
    def test_edge_cases(self):
        # Create data with price oscillating around moving averages
        # This would require specific conditions to be set up to test the edge cases
        pass  # Implement as needed for your scenario


class fetchDataTests(TestCase):
    
    def setUp(self):
     # Clear any existing StockData
        StockData.objects.all().delete()  # Ensure a clean state for each test

    def test_valid_backtest(self):
        response = self.client.get(reverse('fetch_data', kwargs={'symbol': 'AAPL' }))
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
         # Check that data is not None and not empty
        self.assertIsNotNone(data)
        self.assertTrue(data)  # This will pass if data is a non-empty dict or list


    #we can do more test to check if there is maximum 2 years, and more advance Testing
