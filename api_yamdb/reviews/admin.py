from django.contrib import admin

from .models import Category, Review, Genre, Comments, Title, User

admin.site.register(Title)
admin.site.register(Genre)
admin.site.register(Comments)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(User)
