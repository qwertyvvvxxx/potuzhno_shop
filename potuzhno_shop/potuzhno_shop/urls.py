from django.contrib import admin
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from graphene_django.views import GraphQLView
from graphene.validation import depth_limit_validator

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("apps.shop.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("orders/", include("apps.orders.urls")),

    path("api/v1/", include("apps.api.urls")),
    path('api-auth/', include('rest_framework.urls')),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(),
        name="redoc",
    ),
    path(
        "graphql/",
        csrf_exempt(
            GraphQLView.as_view(
                graphiql=True,
                validation_rules=[depth_limit_validator(max_depth=6)]
            )
        )
    ),
]
