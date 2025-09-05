from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name='home'),
    path('country/', country_view, name='country'),
    path('country/details/',get_country_details,name='get_country_details'),
    path('country/edit/<int:id>/',edit_country, name='edit_country'),
    path('country/delete/<int:id>/',delete_country, name='delete_country'),
    
    path('state/', state_view, name='state'),
    path("get_countries_ajax/", get_countries_ajax, name="get_countries_ajax"),
    path("get_state_details/", get_state_details, name="get_state_details"),
    path('state/edit/<int:id>/',edit_state, name='edit_state'),
    path('state/delete/<int:id>/',delete_state, name='delete_state'),
    
    path('city/', city_view, name='city')
]
