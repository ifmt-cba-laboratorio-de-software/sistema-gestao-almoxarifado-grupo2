from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from estoque import views as estoque_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    path('accounts/logout/', estoque_views.logout_view, name='logout'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('estoque.urls')),
]
