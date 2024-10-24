# Import necessary libraries
import pandas as pd
import numpy as np
import requests
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#Code used in google colab to create the pkl model.

# Step 1: Fetch Data from Alpha Vantage
api_key = 'demo'  # We use the demo to train our ML
symbol = 'MBG.DEX'
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
response = requests.get(url)
data = response.json()
raw_data = data['Time Series (Daily)']

# Step 2: Preprocess the Data
df = pd.DataFrame(raw_data).T
df = df.rename(columns={
    '1. open': 'Open',
    '2. high': 'High',
    '3. low': 'Low',
    '4. close': 'Close',
    '5. volume': 'Volume'
})

end_date = datetime.now()
start_date = end_date - timedelta(days=3*365)  # 3 years only to not overTraining our IA
df = df[(df.index >= start_date.strftime('%Y-%m-%d')) & (df.index <= end_date.strftime('%Y-%m-%d'))]

df = df.astype(float)
df = df[['Close']]  # We'll only use 'Close' for prediction
df = df.sort_index()  # Sort by date

# Step 3: Create Features and Target
df['Return'] = df['Close'].pct_change()
df['Lag1'] = df['Close'].shift(1)
df = df.dropna()
X = df[['Lag1']]
y = df['Close']

# Step 4: Build and Train the Linear Regression Model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
model = LinearRegression()
model.fit(X_train, y_train)

# Step 5: Predictions
y_pred = model.predict(X_test)

# Calculate Mean Squared Error
mse = mean_squared_error(y_test, y_pred)

# Step 6: Plotting the actual vs predicted prices
plt.figure(figsize=(14, 7))
plt.plot(df.index[-len(y_test):], y_test, label='Actual Stock Price', color='blue')
plt.plot(df.index[-len(y_test):], y_pred, label='Predicted Stock Price', color='orange')
plt.title('Stock Price Prediction with Linear Regression')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.legend()
plt.show()

#Save our model : 
import joblib
joblib.dump(model, 'linear_regression_model_Stocks.pkl')
