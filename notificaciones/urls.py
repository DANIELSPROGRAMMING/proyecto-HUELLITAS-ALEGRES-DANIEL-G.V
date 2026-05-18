from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    path('marcar-leido/<int:pk>/', views.marcar_leido, name='marcar_leido'),
    path('marcar-todos-leido/', views.marcar_todos_leido, name='marcar_todos_leido'),
    path('listar/', views.listar_notificaciones, name='listar'),
]