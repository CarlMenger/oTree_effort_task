from os import environ


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config["participation_fee"]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=5.00, participation_fee=50.00, doc="", use_browser_bots=False, conversion_rate=0.50,
)

SESSION_CONFIGS = [
     dict(
        name="effort_task_demo_1",
        display_name="Experiment_demo",
        num_demo_participants=2,
        app_sequence=['effort'],
        treatment="0",
        participation_fee=50,
        conversion_rate=0.50,
     ),
    dict(
        name="effort_task_demo_2",
        display_name="Experiment_demo_2",
        num_demo_participants=2,
        app_sequence=['effort'],
        treatment="1",
        conversion_rate=0.50

    ),
]


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "CZK"
USE_POINTS = True

ROOMS = [
    dict(
        name='effort_room_demo',
        display_name='Effort_room_test',
        participant_label_file='_rooms/participant_label_file.txt',
        use_secure_urls=False
    ),
]
OTREE_AUTH_LEVEL = "STUDY"
ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "#n38c)phqy1^2qhv8pk18i_3v9b%#n+*y__@611$a+s#$&a4ao"

# if an app is included in SESSION_CONFIGS, you don"t need to list it here
INSTALLED_APPS = ["otree"]
