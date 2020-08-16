from os import environ

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config["participation_fee"]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=50.00, doc="", use_browser_bots=False
)

SESSION_CONFIGS = [
     dict(
        name="effort_task",
        display_name="Experiment",
        num_demo_participants=2,
        app_sequence=['effort'],
     ),
]


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = "en"

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = "USD"
USE_POINTS = True

ROOMS = []

ADMIN_USERNAME = "admin"
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = "ztreesucks"
    #environ.get("OTREE_ADMIN_PASSWORD")

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = "#n38c)phqy1^2qhv8pk18i_3v9b%#n+*y__@611$a+s#$&a4ao"

# if an app is included in SESSION_CONFIGS, you don"t need to list it here
INSTALLED_APPS = ["otree"]
