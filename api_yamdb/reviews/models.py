import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

VALUE = (
    (1, "Score 1"),
    (2, "Score 2"),
    (3, "Score 3"),
    (4, "Score 4"),
    (5, "Score 5"),
    (6, "Score 6"),
    (7, "Score 7"),
    (8, "Score 8"),
    (9, "Score 9"),
    (10, "Score 10"),
)


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = (
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    email = models.EmailField(
        verbose_name='E-mail address',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Username',
        max_length=150,
        blank=True,
        unique=True
    )
    role = models.CharField(
        verbose_name='Role',
        max_length=50,
        choices=ROLES,
        default=USER
    )
    bio = models.TextField(
        verbose_name='Biography',
        blank=True,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            )
        ]

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN


class Category(models.Model):
    name = models.CharField(verbose_name='Name of category', max_length=256)
    slug = models.SlugField(verbose_name='Slug of category', unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(verbose_name='Name of genre', max_length=256)
    slug = models.SlugField(verbose_name='Slug of genre', unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


def validate_year(value):
    if value > datetime.datetime.now().year:
        raise ValidationError('Incorrect year')


class Title(models.Model):
    name = models.CharField(verbose_name='Name', max_length=256)
    year = models.PositiveSmallIntegerField(verbose_name='Year of issue',
                                            validators=[validate_year])
    description = models.TextField(verbose_name='Description', blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name='Category',
        on_delete=models.CASCADE,
        related_name='titles'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Genre',
        db_index=True,
        related_name='titles'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name


class Review(models.Model):
    text = models.TextField(verbose_name='Review text')
    score = models.PositiveSmallIntegerField(
        verbose_name='Score',
        choices=VALUE)
    pub_date = models.DateTimeField(
        verbose_name='Publication date',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Author',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Title',
        on_delete=models.CASCADE,
        related_name='review',
        null=True
    )

    class Meta:
        verbose_name = 'Review'
        ordering = ('pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]

    def __str__(self):
        return self.text


class Comments(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Author',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Comment text', )
    pub_date = models.DateTimeField(
        verbose_name='Date added',
        auto_now_add=True,
        db_index=True
    )
    review = models.ForeignKey(
        Review,
        verbose_name='Review',
        on_delete=models.CASCADE,
        related_name='comments',
        null=True
    )

    class Meta:
        verbose_name = 'Comment'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text
