# dit-msk
## Информация об API

> Примечание: Список всех конференц-залов зашит 
в кастомную миграцию, что бы не тратить время на их создание

> Примечание: Бронирование конференц-залов можно от часа,
поэтому если пользователь ставит время бронирования 
с 7:00 до 7:30, то бэкенд округлит его бронь до 7:59

> Примечание: Бронирование на несколько часов работает
по такому же принципу

> Примечание: Забронировать конференц-зал можно с 7:00 до 23:00 текущего дня

Одни ручки имеют общий доступ 🟢, 
другие доступны только авторизированному пользователю 🔴

- 🟢 `/api/register/` - Ручка для создания пользователя 
- 🟢 `/api/login/` - Ручка для аутентификации пользователя и 
получения токена
- 🟢 `/api/rooms/` - Ручка для получения списка 
всех конференц-залов в офисе
- 🟢`/api/bookings/<int:pk>/` - Ручка для получения списка возможной брони 
конференц-зала по часам с пометкой, какие часы заняты, а какие свободны
- 🔴`/api/bookings/create/` - Ручка для создания брони
- 🔴`/api/bookings/create/multiple/` - Ручка для создания сразу нескольких бронирований
- 🔴`/api/bookings/cancel/<int:pk>/` - Ручка для отмены бронирования
- 🔴`/api/report/` - Ручка для создания celery задачи по формированию отчета, 
может формировать отчет, как за определённое время, так и для определенного зала
- 🔴`/api/report/download/<str:task_id>/` - Ручка для скачивания отчета

---
## Запуск с помощью Docker

- Перейти в директорию `meeting_room_booking` с помощью команды `cd dit-msk/meeting_room_booking`
- `.env` файл находится в директории 
- Запустить команду `make build`
- Запустить команду `make migrate`
- Запустить команду `make createsuperuser` по необходимости
- Запустить команду `make run`  
- Запустить команду `make celery` 
- Тестирование происходит с помощью команды `make test`

Доступ к документации происходит по ссылке <http://localhost:8000/docs/>

Сохранённые отчеты находятся в папке `media`

---
## Запуск локально

- В `.env` файле нужно изменить `REDIS_HOST` на `localhost`
- Запустить команду `make create_init`
- Запустить команду `make createsuperuser-local` по необходимости 
- Запустить команду `make run-local`
- В новом терминале перейти в `cd dit-msk/meeting_room_booking` 
- Запустить команду `make celery-local` 
- В новом терминале перейти в `cd dit-msk/meeting_room_booking` 
- Тестирование `make test-local` 

Доступ к документации происходит по ссылке <http://localhost:8000/docs/>

Сохранённые отчеты находятся в папке `media`




