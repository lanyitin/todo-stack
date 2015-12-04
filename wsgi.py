import os

def application(environ, start_response):
# explicitly set environment variables from the WSGI-supplied ones
        ENVIRONMENT_VARIABLES = [
        'STACKTODOS_MYSQL_DB_USERNAME',
        'STACKTODOS_MYSQL_DB_PASSWORD',
        'STACKTODOS_MYSQL_DB_HOST',
        'STACKTODOS_MYSQL_DB_PORT',
        'STACKTODOS_SOCIAL_FACEBOOK_KEY',
        'STACKTODOS_SOCIAL_FACEBOOK_SECRET'
        ]
        for key in ENVIRONMENT_VARIABLES:
                if environ.get(key) is None:
                        print key
                else:
                        os.environ[key] = environ.get(key)

        # return app(environ, start_response)
        from app import app
        return app(environ, start_response)