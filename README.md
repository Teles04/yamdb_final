# yamdb_final
yamdb_final

## Cтек используемых технологий:
- Django
- Python
- Postgres
- Docker
- Gunicorn
- Nginx

## Краткое описание проекта:
Проект YaMDb собирает отзывы (Review) пользователей на произведения (Title). Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен администратором (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»).
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
В каждой категории есть произведения: книги, фильмы или музыка. Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Насекомые» и вторая сюита Баха.
Произведению может быть присвоен жанр (Genre) из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). Новые жанры может создавать только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы (Review) и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.*

## Шаблон наполнения env-файла:
'''
DB_ENGINE=django.db.backends.postgresql
DB_NAME=db_name
POSTGRES_USER=user_name
POSTGRES_PASSWORD=db_password
DB_HOST=db
DB_PORT=port_number
SECRET_KEY=(str, 'secret_key')
'''

## Команды для запуска приложения в контейнерах:
'''
docker-compose up
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
'''

## Команда для заполнения базы данных:
'''
python manage.py loaddata dump.json 
'''

## Документация для использования API
После запуска проекта документация по использвоанию API доступна по адресу 
'''
IP_ADDRESS_PROJECT\redoc
'''


![example workflow](https://github.com/teles04/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
