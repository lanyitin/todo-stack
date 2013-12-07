from setuptools import setup

setup(
        name='Stack Todos',
        version='1.0',
        description='A simple todo mamange app',
        author='Lan, Yi-Tin',
        author_email='lanyitin@gmail.com',
        url='http://www.python.org/sigs/distutils-sig/',
        install_requires= ["Flask==0.10.1", "Flask-Assets==0.8", "Jinja2==2.7.1", "MarkupSafe==0.18", "Werkzeug==0.9.4", "cssmin==0.2.0", "gevent==1.0", "greenlet==0.4.1", "itsdangerous==0.23", "jsmin==2.0.8", "pymongo==2.6.3", "webassets==0.8", "wsgiref==0.1.2"]
)
