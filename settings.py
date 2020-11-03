import os
from os import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config["participation_fee"]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.00, participation_fee=0.00, doc="", use_browser_bots=False, conversion_rate=0.00,
    winning_bonus=50.00, file_dir=["effort", "data"], resultsPage_timeout=30, generate_payfile=False,
    add_to_central_DB=True,

)

SESSION_CONFIGS = [
    dict(
        name="effort_task_treatment_0_control",
        display_name="Effort_task_T0_noInfo_control",
        num_demo_participants=2,
        app_sequence=['effort'],
        treatment=0,

    ),
    dict(
        name="effort_task_treatment_1",
        display_name="Effort_task_T1_oneWayInfo",
        num_demo_participants=2,
        app_sequence=['effort'],
        treatment=1,
        pairing_filter_margin=2,

    ),
    dict(
        name="effort_task_treatment_2",
        display_name="Effort_task_T2_bothWayInfo",
        num_demo_participants=2,
        app_sequence=['effort'],
        treatment=2,
        pairing_filter_margin=2,

    ),
    dict(
        name="veronika_test",
        display_name="Veronika",
        num_demo_participants=1,
        app_sequence=['Veronika'],

    ),
]


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en-us"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "CZK"
USE_POINTS = False

ROOMS = [
    dict(
        name='Effort_task_Both_Hanzlik',
        display_name='Effort_task_Both_Hanzlik',
        participant_label_file='_rooms/participant_label_file.txt',
        use_secure_urls=False,
    ),
]
#OTREE_AUTH_LEVEL = "STUDY"
ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "#n38c)phqy1^2qhv8pk18i_3v9b%#n+*y__@611$a+s#$&a4ao"

# if an app is included in SESSION_CONFIGS, you don"t need to list it here
INSTALLED_APPS = ["otree"]

#DATABASE_URL = "postgres://postgres@localhost/django_db"
#REDIS_URL = "redis://localhost:6379"

"""environ["DATABASE_URL"] = "postgres://postgres@localhost/django_db"
environ["REDIS_URL"] = "redis://localhost:6379"
environ["OTREE_ADMIN_PASSWORD"] = "odraSe5ku"
environ["OTREE_AUTH_LEVEL"] = "STUDY" 
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/effort/data")]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = "/static/" """

if environ.get('OTREE_PRODUCTION') not in {None, '', '0'}:
    DEBUG = False
else:
    DEBUG = True

environ["OTREE_AUTH_LEVEL"] = "STUDY"
environ["OTREE_ADMIN_PASSWORD"] = "odraSe5ku"
PRODUCTION = 1
