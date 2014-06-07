import os

class Config:
    SECRET_KEY = 'e6cb00fb23790ba6d43de3826639aae2'

    db_connection_str = 'mysql+mysqlconnector://{0}:{1}@{2}:{3}' \
        '/stacktodos?collation=utf8_general_ci&use_unicode=true&charset=utf8'

    SQLALCHEMY_DATABASE_URI = db_connection_str.format(
        os.environ['STACKTODOS_MYSQL_DB_USERNAME'],
        os.environ['STACKTODOS_MYSQL_DB_PASSWORD'],
        os.environ['STACKTODOS_MYSQL_DB_HOST'],
        os.environ['STACKTODOS_MYSQL_DB_PORT'],
    )

    SOCIAL_FACEBOOK_KEY = ""
    SOCIAL_FACEBOOK_SECRET = ""


class DevelopConfig(Config):
    DEBUG = True
    SOCIAL_FACEBOOK_KEY = '1594660774091682'
    SOCIAL_FACEBOOK_SECRET = 'd18dd1548690f65b8b2fbb17becaf93b'

class ProductionConfig(Config):
    SOCIAL_FACEBOOK_KEY = os.environ['STACKTODOS_SOCIAL_FACEBOOK_KEY']
    SOCIAL_FACEBOOK_SECRET = os.environ['STACKTODOS_SOCIAL_FACEBOOK_SECRET']
