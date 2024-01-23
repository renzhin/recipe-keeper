from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import BlacklistMixin, RefreshToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    FollowSerializer,
    RecipeSerializer,
    IngredientSerializer,
    MeasurementSerializer,
    TagSerializer,
    FavouriteSerializer,
    ShoplistSerializer,
    CurrentUserSerializer,
)
from recipes.models import (
    Follow, Tag, Measurement, Ingredient, Recipe, Favourite, Shoplist
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({
            'auth_token': str(access_token),
        })


# class LogoutView(APIView):
#     permission_classes = (IsAuthenticated,)

#     def post(self, request):
#         try:
#             access_token = self.extract_access_token(request)
#             if not access_token:
#                 raise TokenError('Access token is required in the request header')

#             # Черный список access токена
#             token = OutstandingToken.objects.filter(token=access_token).first()
#             if token:
#                 token.blacklist()

#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except TokenError as e:
#             return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

#     def extract_access_token(self, request):
#         auth_header = request.headers.get('Authorization', '')

#         # Проверяем наличие префикса "Bearer "
#         if auth_header.startswith('Bearer '):
#             return auth_header.split('Bearer ')[1].strip()

#         # Проверяем наличие префикса "Token "
#         elif auth_header.startswith('Token '):
#             return auth_header.split('Token ')[1].strip()

#         return None


class LogoutView(BlacklistMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            access_token = self.extract_access_token(request)
            if not access_token:
                raise TokenError('Access token is required in the request header')
            print(f'извлек токен {access_token}')
            # Вместо вызова blacklist, используйте BlacklistMixin
            self.blacklist(access_token)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError as e:
            return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    def extract_access_token(self, request):
        auth_header = request.headers.get('Authorization', '')

        # Проверяем наличие префикса "Bearer "
        if auth_header.startswith('Bearer '):
            return auth_header.split('Bearer ')[1].strip()

        # Проверяем наличие префикса "Token "
        elif auth_header.startswith('Token '):
            return auth_header.split('Token ')[1].strip()

        return None


# class LogoutView(BlacklistMixin, APIView):
#     permission_classes = (IsAuthenticated,)

#     def post(self, request):
#         try:
#             access_token = self.extract_access_token(request)
#             if not access_token:
#                 raise TokenError('Access token is required in the request header')

#             # Вместо вызова blacklist, используйте BlacklistMixin
#             self.add_to_blacklist(access_token)
            
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except TokenError as e:
#             return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

#     def extract_access_token(self, request):
#         auth_header = request.headers.get('Authorization', '')

#         # Проверяем наличие префикса "Bearer "
#         if auth_header.startswith('Bearer '):
#             return auth_header.split('Bearer ')[1].strip()

#         # Проверяем наличие префикса "Token "
#         elif auth_header.startswith('Token '):
#             return auth_header.split('Token ')[1].strip()

#         return None


# class LogoutView(APIView):
#     permission_classes = (IsAuthenticated,)

#     def post(self, request):
#         try:
#             # Используем метод split() для разделения строки на две части по пробелу
#             authorization_header = request.headers.get('Authorization', '')
#             _, token = authorization_header.split() if ' ' in authorization_header else ('', '')

#             if not token:
#                 raise Exception('Authorization header with Bearer token is required')

#             RefreshToken(token).blacklist()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except Exception as e:
#             return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        return self.request.user


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination


class IngredientViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class MeasurementViewSet(viewsets.ModelViewSet):
    serializer_class = MeasurementSerializer
    queryset = Measurement.objects.all()


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class FavouriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavouriteSerializer
    queryset = Favourite.objects.all()


class ShoplistViewSet(viewsets.ModelViewSet):
    serializer_class = ShoplistSerializer
    queryset = Shoplist.objects.all()
