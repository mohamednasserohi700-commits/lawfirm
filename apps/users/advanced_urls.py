from django.urls import path

from .advanced_views import advanced_index, advanced_page


urlpatterns = [
    path("", advanced_index, name="advanced_index"),
    path("<slug:page_key>/", advanced_page, name="advanced_page"),
]
