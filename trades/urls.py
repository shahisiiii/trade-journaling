from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.trade_list, name='trade_list'),
    path('add/', views.trade_create, name='trade_create'),
    path('<int:pk>/', views.trade_detail, name='trade_detail'),
    path('<int:pk>/edit/', views.trade_update, name='trade_update'),
    path('<int:pk>/delete/', views.trade_delete, name='trade_delete'),
    path('merge/', views.merge_trades, name='merge_trades'),
    path('<int:pk>/unmerge/', views.unmerge_trade, name='unmerge_trade'),
    path('export/csv/', views.export_trades_csv, name='export_trades_csv'),
    path('import/csv/', views.import_trades_csv, name='import_trades_csv'),
]