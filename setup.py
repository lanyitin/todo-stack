from setuptools import setup

setup(name='Stack Todos',
      version='1.0',
      description='A simple todo mamange app',
      author='Lan, Yi-Tin',
      author_email='lanyitin@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['Flask', 'Flask-Assets', 'cssmin', 'jsmin', 'MarkupSafe', 'pymongo'],
     )
