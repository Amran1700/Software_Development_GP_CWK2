from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from global_feature import views as global_views

urlpatterns = [
    path("", global_views.home, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("global_feature.urls")),
    path("messages/", include("messages_feature.urls")),
    path("", include("organisation_feature.urls")),
    path("reports/", include("reports_feature.urls")),
    path("schedule/", include("schedule_feature.urls")),
    path("teams/", include("teams_feature.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")