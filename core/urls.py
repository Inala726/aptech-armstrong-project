from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register),
    path('auth/login/', views.login_view),

    path('profile/', views.profile),
    path('profile/address/', views.add_address),

    path('armstrong/check/', views.check_single),
    path('armstrong/range/', views.check_range),

    path('attempts/', views.attempt_history),

    path('feedback/', views.submit_feedback),
    path('contact/', views.contact_us),
]