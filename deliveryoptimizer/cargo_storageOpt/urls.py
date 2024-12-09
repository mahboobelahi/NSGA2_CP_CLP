from django.urls import path
from .views.get_views import *
from .views.post_views import *


app_name = 'cargo_storageOpt'

urlpatterns = [
    #! routes for testing
    path('', current_datetime, name='test'),
    
    #* get routes
    path('getids/', get_cont_ids, name='get_cont_ids'),
    path('get-result-files/', get_all_results_files,
         name=' get_all_results_files'),
    path('get-results/', get_results, name='get-results'),
    path('container/<str:container_id>/',
         get_container_info, name='get_container_info'),
    
    #? post routes
    path('submit-order-info/', submit_order_info, name='order_info'),
    path('compute-clp/', compute, name='compute'),
    path('historic_plot_data/', historic_plot_data, name='historic_plot_data'),
    path('gen-report/', generate_report, name='generate_report'),
    
    #* Ar and plotly 
    path('ar-view/', handle_ar_view, name='handle_ar_view'),
    path('plotly-vis/', handle_plot_data, name='handle_plot_data'),
    
]
