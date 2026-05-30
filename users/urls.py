from django.urls import path
from .views import register_view, login_view, logout_view, dashboard_view, profile_edit_view, become_teacher_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
    path('become-teacher/', become_teacher_view, name='become_teacher'),
]
