from django.urls import path
from .views import fetch_data
from .views import backtest_strategy
from .views import generate_backtest_report

urlpatterns = [
    path('fetch/<str:symbol>/', fetch_data, name='fetch_data'),
]

urlpatterns += [
    path('backtest/<str:symbol>/<int:initial_investment>/', backtest_strategy, name='backtest_strategy'),
]

urlpatterns += [
    path('generatebacktestreport/<str:symbol>/<int:initial_investment>/', generate_backtest_report, name='generate_backtest_report'),
]



