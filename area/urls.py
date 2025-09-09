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
    
    path('city/', city_view, name='city'),
    path('get_states_ajax/<int:country_id>/', get_states_ajax, name='get_states_ajax'),
    path('city/details/',get_city_details, name='get_city_details'),
    path('city/edit/<int:id>/', edit_city, name='edit_city'),
    path('city/delete/<int:id>/',delete_city, name='delete_city'),
    
    path("ajax/check-state-unique/", ajax_check_state_unique, name="ajax_check_state_unique"),
    path("validate_city_edit/", validate_city_edit, name="validate_city_edit"),
]
