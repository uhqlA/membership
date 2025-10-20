from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# router.register(r'members', views.MemberViewSet, basename='member')  # COMMENTED OUT

app_name = 'membership'

urlpatterns = [
    # path('', include(router.urls)),  # COMMENTED OUT
    path('register/', views.register_member, name='register'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('member/<str:membership_number>/', views.member_details, name='member_details'),
    path('certificate/<str:membership_number>/', views.download_certificate_by_number, name='download_certificate'),
]