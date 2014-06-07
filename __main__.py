# -*- coding: utf-8 -*-
from flask.ext.script import Manager
from app import app

manager = Manager(app)
manager.run()
