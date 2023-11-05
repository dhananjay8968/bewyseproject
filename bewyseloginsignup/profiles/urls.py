from django.urls import path
from profiles.views import view_profile,edit_profile

urlpatterns = [
    path("accounts/profile/view",view_profile),
    path("accounts/profile/edit",edit_profile),
]