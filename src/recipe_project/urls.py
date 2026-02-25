from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth import views as auth_views
from recipes import views as recipe_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # App URLs
    path("", include("recipes.urls")),

    # Auth URLs
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Logged out success page
    path("success/", recipe_views.logout_success, name="logout_success"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)