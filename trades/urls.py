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
    
    # Events URLs
    path('events/', views.events_list, name='events_list'),
    path('events/add/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Achievements URLs
    path('achievements/', views.achievements_list, name='achievements_list'),
    path('achievements/add/', views.achievement_create, name='achievement_create'),
    path('achievements/<int:pk>/edit/', views.achievement_update, name='achievement_update'),
    path('achievements/<int:pk>/delete/', views.achievement_delete, name='achievement_delete'),
    
    # AJAX endpoints
    path('calendar-data/', views.get_calendar_data, name='calendar_data'),
    path("keep-alive/", views.keep_alive, name="keep_alive"),
]

