from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),  # Para atualizar o perfil
    path('logout/', views.logout_view, name='logout'),

]