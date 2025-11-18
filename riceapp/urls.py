from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('classify/', views.classify_rice_disease, name='classify_rice_disease'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('history/', views.classification_history, name='classification_history'),
    path('history/<int:result_id>/', views.classification_result_detail, name='classification_result_detail'),
]

