from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomTokenObtainPairView, LogoutView, CurrentUserView
from .views import UserViewSet, RecipeViewSet, FollowViewSet, IngredientViewSet


app_name = 'api'


v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet)
v1_router.register(r'recipes', RecipeViewSet)
v1_router.register(r'follows', FollowViewSet)
v1_router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path(
        'auth/token/login/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'auth/token/logout/',
        LogoutView.as_view(),
        name='token_logout'
    ),
    path(
        'users/me/',
        CurrentUserView.as_view(),
        name='current_user'
    ),
    path('', include(v1_router.urls)),
]


# urlpatterns = [
#     path('v1/auth/signup/', SignUpView.as_view()),
#     path('auth/token/login/', TokenView.as_view()),
# ]