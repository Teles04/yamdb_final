from rest_framework import routers
from django.urls import path, include
from api.views import (
    UserViewSet,
    get_jwt_token,
    register,
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentsViewSet
)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='user')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>[\d/]+)/reviews',
    ReviewViewSet,
    basename='review')
router_v1.register(
    r'titles/(?P<title_id>[\d/]+)/reviews/(?P<review_id>[\d/]+)/comments',
    CommentsViewSet,
    basename='comments'
)

url_pat_auth = [
    path('signup/', register, name='register'),
    path('token/', get_jwt_token, name='token'),
]

urlpatterns = [
    path('v1/auth/', include(url_pat_auth)),
    path('v1/', include(router_v1.urls)),
]
