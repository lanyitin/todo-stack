from __future__ import print_function
import unittest, os, sys, sqlite3
sys.path.append(os.path.abspath("."))
from app.Mappers import SqliteStackMapper, MapperFactory, MongoStackMapper
class MapperFactoryTest(unittest.TestCase):
	def testGetMongoMapper(self):
		factory = MapperFactory("mongo")
		mapper = factory.getMapper();
		self.assertEquals(MongoStackMapper, mapper)
	def testGetSqliteMapper(self):
		factory = MapperFactory("sqlite")
		mapper = factory.getMapper();
		self.assertEquals(SqliteStackMapper, mapper)
