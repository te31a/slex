from django.urls import path, include

from base_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('<slug:_filial_slug>/', views.home_filial, name='main_filial'),
    path('<slug:_filial_slug>/contracts/', views.list_view_contracts, name='contracts'),
    path('<slug:_filial_slug>/contracts/<slug:_contract_slug>/', views.detail_view_contracts, name='detail_contract'),

    # path('filial-detail/<slug:slug>/', views.FilialDetail.as_view(), name='filial-detail'),
    path('<slug:_filial_slug>/contracts/<slug:_contract_slug>/handler_form/', views.handler_data_form,
         name='handler_form'),

    path('accounts/login/', views.NotFound.as_view(), name='not_groups'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
