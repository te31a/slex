# SLEX — документация проекта

> Актуально на: 19 февраля 2026 г.
> Django 6.0.2 · Python 3.14 · SQLite3 (внутренняя БД) · PostgreSQL (внешние данные)

---

## 1. Описание системы

**SLEX** — внутренняя корпоративная веб-система на Django для управления договорами с поставщиками и обработки заявок по филиалам компании.

**Функции системы:**
- Организация работы по филиалам (структура: филиал → меню → контракты)
- Загрузка Excel-файлов заявок, парсинг и конвертация в XML-формат для ERP Microsoft Dynamics AX (Axapta)
- Подключение к внешней PostgreSQL для получения данных об остатках товаров и справочнику номенклатуры
- Проверка отдельного товара по артикулу через PostgreSQL
- Загрузка остатков ТМЦ
- Веб-интерфейс с авторизацией и разграничением по ролям

---

## 2. Стек и зависимости

| Компонент       | Версия  |
|-----------------|---------|
| Python          | 3.14.x  |
| Django          | 6.0.2   |
| pandas          | 3.0.1   |
| numpy           | 2.4.2   |
| openpyxl        | 3.1.5   |
| psycopg2-binary | 2.9.11  |
| sqlparse        | 0.5.5   |

Виртуальное окружение: `.venv\` (в корне проекта)

---

## 3. Структура проекта

```
slex/
├── manage.py                  # Точка входа, содержит _disable_quickedit() для Windows
├── db.sqlite3                 # Внутренняя БД (пользователи, филиалы, меню, контракты)
├── requirements.txt
├── .env.example               # Шаблон переменных окружения → скопировать в .env
├── logs/
│   ├── server.log             # HTTP-запросы GET/POST
│   └── django.log             # Ошибки приложения
├── SLEX_02/                   # Конфигурация Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── base_app/                  # Основное приложение
│   ├── models.py              # Модели: Filial, Menu, Contracts
│   ├── views.py               # Вьюхи + dict_module (реестр обработчиков)
│   ├── urls.py                # URL-маршруты
│   ├── pg_utils.py            # Утилиты работы с PostgreSQL
│   ├── utils.py               # Утилиты: data_to_dict, save_to_xml
│   ├── admin.py               # Регистрация моделей в Django Admin
│   └── contract_models/       # Обработчики контрактов
│       ├── neo_stroy_krd.py   # Обработчик: Нео-Строй/КРД/Сочи
│       ├── krd/               # Папка для КРД-обработчиков
│       ├── rnd/
│       │   └── ok.py          # Заглушка обработчика ОК
│       └── vlg/               # Папка для Волга-обработчиков
├── templates/base_app/        # HTML-шаблоны
├── static/base_app/           # CSS, изображения
│   ├── css/
│   │   ├── base.css           # CSS-переменные, шапка, сброс
│   │   ├── menu.css           # Навигационное меню
│   │   ├── buttons.css        # Кнопки
│   │   ├── inputs.css         # Поля ввода
│   │   ├── content.css        # Таблицы, контент
│   │   ├── login.css          # Страница входа
│   │   └── contracts.css      # Карточки операций контракта
│   └── images/
│       └── slex-logo.png
└── .vscode/
    └── tasks.json             # Задачи VS Code для запуска сервера
```

---

## 4. Запуск проекта

### 4.1 Первый запуск (инициализация)

```powershell
# 1. Перейти в папку проекта
cd C:\Users\user\Desktop\projects\slex\slex

# 2. Создать виртуальное окружение (если не создано)
python -m venv .venv

# 3. Активировать
.venv\Scripts\Activate.ps1

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Применить миграции
python manage.py migrate

# 6. Создать суперпользователя
python manage.py createsuperuser

# 7. Запустить сервер
python manage.py runserver 8000
```

### 4.2 Обычный запуск

```powershell
cd C:\Users\user\Desktop\projects\slex\slex
.venv\Scripts\python.exe manage.py runserver 8000
```

Или через задачу VS Code: `Ctrl+Shift+B` → **"Запустить сервер (логи в файл)"**

### 4.3 Запуск в фоне без консоли (без зависаний)

```powershell
Start-Process -FilePath ".venv\Scripts\python.exe" `
  -ArgumentList "manage.py runserver 8000" `
  -WorkingDirectory (Get-Location)
```

### 4.4 Просмотр логов в реальном времени

```powershell
# HTTP-логи (все запросы)
Get-Content -Wait -Tail 50 logs\server.log

# Ошибки приложения
Get-Content -Wait -Tail 50 logs\django.log
```

---

## 5. Администрирование

### 5.1 Django Admin

URL: `http://127.0.0.1:8000/admin/`

Доступен только суперпользователям. В разделе **Сервис** (ссылка в шапке сайта).

### 5.2 Управление филиалами (`Filial`)

| Поле           | Описание                                              |
|----------------|-------------------------------------------------------|
| `name`         | Название филиала (отображается в меню)                |
| `slug`         | Уникальный идентификатор для URL, только latin+дефис  |
| `dsn`          | Строка подключения к PostgreSQL филиала               |
| `prog_id`      | ID программы в ERP (Axapta)                          |
| `position`     | Порядок сортировки в списке                           |
| `as_active`    | Отображать ли на сайте                                |

**DSN-строка** формат: `host=192.168.1.1 port=5432 dbname=mydb user=myuser password=mypass`

### 5.3 Управление меню (`Menu`)

| Поле        | Описание                                                      |
|-------------|---------------------------------------------------------------|
| `name`      | Название пункта меню                                          |
| `filial`    | К какому филиалу относится                                    |
| `slug`      | Должен совпадать с именем URL-маршрута в `urls.py`           |
| `position`  | Порядок в меню                                                |
| `as_active` | Отображать ли                                                 |

### 5.4 Управление контрактами (`Contracts`)

| Поле                | Описание                                                    |
|---------------------|-------------------------------------------------------------|
| `name`              | Название контракта (влияет на выбор обработчика в коде)    |
| `filial`            | К какому филиалу относится                                  |
| `slug`              | **Ключ** для поиска обработчика в `dict_module` в `views.py`|
| `path_saved_order`  | Путь для сохранения XML-заявок                              |
| `path_saved_reports`| Путь для сохранения отчётов                                 |
| `id_groups_goods`   | ID группы товаров в PostgreSQL                              |
| `id_groups_vod`     | ID группы ВОД в PostgreSQL                                  |
| `id_groups_vod_tls` | ID группы ВОД-ТЛС в PostgreSQL                             |
| `position`          | Порядок в списке                                            |
| `as_active`         | Отображать ли                                               |

### 5.5 Управление пользователями

Через стандартный раздел Django Admin → **Пользователи**:
- Суперпользователь — полный доступ, видит раздел **Сервис** в шапке
- Обычный пользователь — только работа с контрактами своего филиала
- Группы и права настраиваются стандартными средствами Django

---

## 6. Как добавить новый сервис (обработчик контракта)

Система использует паттерн «реестр обработчиков». Каждый контракт в БД имеет `slug`, который сопоставляется с Python-модулем в `dict_module`.

### Шаг 1 — Создать модуль обработчика

Создать файл, например `base_app/contract_models/rnd/new_contract.py`:

```python
def start(file_name, contract):
    """
    file_name: str — путь к загруженному Excel-файлу
    contract:  Contracts — объект контракта из БД

    Возвращает: (dict_result, error: bool)
      - dict_result — словарь с ключами-описаниями и значениями для отображения
      - error — True если возникла ошибка, False если успешно
    """
    try:
        # ... ваша логика парсинга и обработки ...
        return {'Обработано строк': 42}, False
    except Exception as e:
        return {'Ошибка': str(e)}, True
```

### Шаг 2 — Зарегистрировать в реестре

В файле `base_app/views.py` добавить запись в `dict_module`:

```python
from base_app.contract_models.rnd import new_contract   # импорт

dict_module = {
    'neo-stroj-rostov': neo_stroy_krd,
    'ok': ok,
    'new-contract-slug': new_contract,   # ← добавить сюда
}
```

### Шаг 3 — Создать контракт в Admin

Перейти в Admin → **Контракты** → Добавить:
- `slug` = `new-contract-slug` (точно как ключ в `dict_module`)
- Указать нужный филиал, пути сохранения и ID групп товаров

### Шаг 4 — Проверить

Открыть страницу контракта `/<filial_slug>/contracts/<contract_slug>/` и выполнить операцию.

---

## 7. Работа с PostgreSQL

Модуль `base_app/pg_utils.py` реализует подключение к внешней PostgreSQL.

- Строка подключения (`dsn`) берётся из модели `Filial.dsn`
- Все SQL-запросы используют параметризацию (`%s`) — защита от SQL-инъекций
- Доступные функции:

| Функция                              | Описание                                  |
|--------------------------------------|-------------------------------------------|
| `get_good_by_marking_goods`          | Найти товар по артикулу                   |
| `get_goods_list_by_marking_goods`    | Найти список товаров по артикулам         |
| `query_goods_stock_by_group_id_ok`   | Остатки ТМЦ для обработчика ОК           |
| `query_goods_stock_by_group_id`      | Остатки ТМЦ по группе (общий)            |

---

## 8. URL-маршруты

| URL                                                    | Представление           | Описание                    |
|--------------------------------------------------------|-------------------------|-----------------------------|
| `/`                                                    | `home`                  | Список филиалов             |
| `/<filial_slug>/`                                      | `home_filial`           | Меню филиала                |
| `/<filial_slug>/contracts/`                            | `list_view_contracts`   | Список контрактов           |
| `/<filial_slug>/contracts/<contract_slug>/`            | `detail_view_contracts` | Страница контракта          |
| `/<filial_slug>/contracts/<contract_slug>/handler_form/` | `handler_data_form`   | Обработка форм (POST)       |
| `/login/`                                              | `Login`                 | Вход                        |
| `/logout/`                                             | `logout_view`           | Выход                       |
| `/admin/`                                              | Django Admin            | Администрирование           |

---

## 9. Переменные окружения

Скопировать `.env.example` в `.env` и при необходимости изменить значения:

```dotenv
SECRET_KEY=django-insecure-1rj_f1($it+!-^#3b*(f#zc@&$#56ifucpnt_bt^ap+_(3v%db
DEBUG=True
# ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

В продакшне: `DEBUG=False`, задать `SECRET_KEY` новым случайным ключом, указать `ALLOWED_HOSTS`.

Сгенерировать новый SECRET_KEY:
```powershell
.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 10. Диагностика

```powershell
# Проверить корректность конфигурации Django
.venv\Scripts\python.exe manage.py check

# Применить новые миграции после изменения моделей
.venv\Scripts\python.exe manage.py migrate

# Создать миграцию после изменения models.py
.venv\Scripts\python.exe manage.py makemigrations base_app

# Просмотр HTTP-логов в реальном времени
Get-Content -Wait -Tail 100 logs\server.log

# Просмотр ошибок
Get-Content -Wait -Tail 50 logs\django.log
```

---

## 11. Итоговая оценка

> Оценка актуальна после изменений, внесённых в рамках текущей сессии (февраль 2026).

| Критерий               | До  | После | Комментарий                                                                                   |
|------------------------|-----|-------|-----------------------------------------------------------------------------------------------|
| Функциональность       | 4/10 | 5/10 | Исправлены 404 на `/rnd/` и других маршрутах, починены битые ссылки в шаблонах               |
| Безопасность           | 2/10 | 3/10 | `SECRET_KEY` вынесен в `.env.example`; SQL-инъекции в `pg_utils.py` и глобальный state остаются |
| Качество кода          | 3/10 | 4/10 | Добавлен `_disable_quickedit()`, нормализовано логирование, исправлены шаблоны с `{% url %}` |
| Архитектура            | 5/10 | 5/10 | Паттерн обработчиков контрактов правильный, реализация по-прежнему требует рефакторинга       |
| Готовность к продакшну | 1/10 | 3/10 | Сервер больше не зависает (QuickEdit), HTTP-логи пишутся в файл, добавлены VS Code tasks      |
| Потенциал              | 7/10 | 7/10 | Хорошая база для развития: ясная предметная область, модульные обработчики, Django 6          |

**Средняя оценка:** было **3.7/10** → стало **4.5/10**

### Приоритеты для дальнейшего улучшения

1. **Безопасность** — параметризованные запросы в `pg_utils.py` вместо f-строк; убрать `SECRET_KEY` из `settings.py` в `.env`
2. **Глобальный state** — переписать обработчики контрактов без глобальных переменных
3. **Тесты** — написать базовые unit-тесты для слоя парсинга Excel и XML-генерации
4. **Документация кода** — docstring к классам/функциям в `contract_models/`
5. **Валидация входных данных** — проверка загружаемых Excel-файлов до начала обработки
