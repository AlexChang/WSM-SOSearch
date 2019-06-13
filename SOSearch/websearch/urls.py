from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('questions/', views.index, name='index'),
    path('questions/<int:question_id>/', views.detail, name='detail'),
    path('search/', views.MySeachView(), name='search'),
]