from django.urls import path
from . import views

urlpatterns = [
    path('climate/metrics/',            views.climate_metrics,    name='api_metrics'),
    path('climate/historical/',         views.historical_data,    name='api_historical'),
    path('climate/region/<str:region>/',views.region_data,        name='api_region'),
    path('climate/regions/',            views.regions_list,       name='api_regions'),
    path('climate/coords/',             views.climate_by_coords,  name='api_coords'),
    path('predictions/temperature/',    views.predict_temperature, name='api_predict_temp'),
    path('predictions/disasters/',      views.predict_disasters,  name='api_predict_disasters'),
    path('simulator/run/',              views.run_simulation,     name='api_simulate'),
    path('time-machine/<int:year>/',    views.time_machine_data,  name='api_time_machine'),
    path('carbon/calculate/',           views.calculate_carbon,   name='api_carbon'),
    path('policy/simulate/',            views.simulate_policy,    name='api_policy'),
    path('rankings/',                   views.country_rankings,   name='api_rankings'),
    path('chat/ask/',                   views.chat_ask,           name='api_chat'),
    path('alerts/',                     views.climate_alerts,     name='api_alerts'),
    path('heatmap/',                    views.disaster_heatmap,   name='api_heatmap'),
    path('geocode/reverse/',            views.reverse_geocode,    name='api_reverse_geocode'),
    path('geocode/search/',             views.geocode_search,     name='api_geocode_search'),
]
