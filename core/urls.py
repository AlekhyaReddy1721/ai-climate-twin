from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('globe/', views.globe, name='globe'),
    path('predictions/', views.predictions, name='predictions'),
    path('disasters/', views.disasters, name='disasters'),
    path('simulator/', views.simulator, name='simulator'),
    path('time-machine/', views.time_machine, name='time_machine'),
    path('carbon/', views.carbon, name='carbon'),
    path('policy/', views.policy, name='policy'),
    path('reports/', views.reports, name='reports'),
    path('rankings/', views.rankings, name='rankings'),
    path('chat/', views.chat, name='chat'),
]
