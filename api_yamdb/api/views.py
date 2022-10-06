from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import viewsets, filters, permissions, status

from api.permissions import (IsAdmin,
                             AdminOrReadOnly,
                             IsAdminModeratorOwnerOrReadOnly)
from api.serializers import (UserSerializer,
                             TokenSerializer,
                             RegisterDataSerializer,
                             UserEditSerializer)
from api.serializers import (CategorySerializer,
                             GenreSerializer,
                             TitleSerializer,
                             ReadTitleSerializer,
                             ReviewSerializer,
                             CommentsSerializer, )
from api.viewsets import ListCreateViewSet
from reviews.models import User
from reviews.models import (Category,
                            Genre,
                            Title,
                            Review,
                            Comments)

from .filters import FilterForTitle


class UserViewSet(viewsets.ModelViewSet):
    """
    Получение списка пользователей.
    """
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin,)

    @action(
        methods=[
            'get',
            'patch',
        ],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def users_own_profile(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """
    Пользователь отправляет POST-запрос на добавление нового пользователя
    с параметрами email и username на эндпоинт /api/v1/auth/signup/.
    YaMDB отправляет письмо с кодом подтверждения (confirmation_code)
    на адрес email.
    """
    serializer = RegisterDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='YaMDb registration',
        message=f'Your confirmation code: {confirmation_code}',
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    """
    Пользователь отправляет POST-запрос с параметрами
    username и confirmation_code на эндпоинт /api/v1/auth/token/,
    в ответе на запрос ему приходит token (JWT-токен).
    """
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )

    if default_token_generator.check_token(
            user, serializer.validated_data['confirmation_code']
    ):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(ListCreateViewSet):
    """
    Получить список всех категорий можно без токена.
    Добавить новую категорию можно только с правами Администратора.
    Удалить категорию может только Администратор.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateViewSet):
    """
    Получить список всех жанров можно без токена.
    Добавить новый жанр можно только с правами Администратора.
    Удалить жанр может только Администратор.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Получить список всех произведений можно без токена.
    Добавить новое призведение можно только с правами Администратора.
    Нельзя добавлять произведения, которые еще не вышли
    (год выпуска не может быть больше текущего).
    При добавлении нового произведения требуется указать уже
    существующие категорию и жанр.
    Получить информацию о произведении можно без токена.
    Обновить информация о произведении может только администратор.
    Удалить произведение может только Администратор.
    """
    queryset = Title.objects.all().annotate(
        Avg('review__score')
    ).order_by('name')
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterForTitle

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleSerializer
        return ReadTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Получить список всех отзывов можно без токена.
    Добавить новый отзыв могут только Аутентифицированные пользователи.
    Пользователь может оставить только один отзыв на произведение.
    Получить отзыв по id для указанного произведения можно без токена.
    Частично обновить отзыв могут только автор отзыва,
    Модератор или Администратор.
    Удалить отзыв могут только автор отзыва, Модератор или Администратор
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        review = Review.objects.filter(title=self.get_title())
        return review

    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(title_id=self.get_title().id, author=author)


class CommentsViewSet(viewsets.ModelViewSet):
    """
    Получить список всех комментариев можно без токена.
    Добавить новый коммент могут только Аутентифицированные пользователи.
    Получить коммент для тзыва по id можно без токена.
    Частично обновить коммент могут только автор отзыва,
    Модератор или Администратор.
    Удалить коммент могут только автор коммента, Модератор или Администратор
    """
    serializer_class = CommentsSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        comments = Comments.objects.filter(review=self.get_review())
        return comments

    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(review_id=self.get_review().id, author=author)
