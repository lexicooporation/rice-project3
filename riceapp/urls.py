from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('classify/', views.classify_rice_disease, name='classify_rice_disease'),
    path('history/', views.classification_history, name='classification_history'),
    path('history/<int:result_id>/', views.classification_result_detail, name='classification_result_detail'),
]

