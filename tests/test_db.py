# $Id: test_db.py,v 1.6 2001/07/27 06:23:59 richard Exp $ 

import unittest, os, shutil

from roundup.backends import anydbm
from roundup.hyperdb import String, Link, Multilink, Date, Interval, Class, \
    DatabaseError

def setupSchema(db, create):
    status = Class(db, "status", name=String())
    status.setkey("name")
    if create:
        status.create(name="unread")
        status.create(name="in-progress")
        status.create(name="testing")
        status.create(name="resolved")
    Class(db, "user", username=String(), password=String())
    Class(db, "issue", title=String(), status=Link("status"),
        nosy=Multilink("user"))

class DBTestCase(unittest.TestCase):
    def setUp(self):
        class Database(anydbm.Database):
            pass
        # remove previous test, ignore errors
        if os.path.exists('_test_dir'):
            shutil.rmtree('_test_dir')
        os.mkdir('_test_dir')
        self.db = Database('_test_dir', 'test')
        setupSchema(self.db, 1)

    def tearDown(self):
        self.db.close()
        shutil.rmtree('_test_dir')

    def testChanges(self):
        self.db.issue.create(title="spam", status='1')
        self.db.issue.create(title="eggs", status='2')
        self.db.issue.create(title="ham", status='4')
        self.db.issue.create(title="arguments", status='2')
        self.db.issue.create(title="abuse", status='1')
        self.db.issue.addprop(fixer=Link("user"))
        props = self.db.issue.getprops()
        keys = props.keys()
        keys.sort()
        self.assertEqual(keys, ['fixer', 'nosy', 'status', 'title'])
        self.db.issue.set('5', status='2')
        self.db.issue.get('5', "status")
        self.db.status.get('2', "name")
        self.db.issue.get('5', "title")
        self.db.issue.find(status = self.db.status.lookup("in-progress"))
        self.db.issue.history('5')
        self.db.status.history('1')
        self.db.status.history('2')

    def testExceptions(self):
        # this tests the exceptions that should be raised
        ar = self.assertRaises

        #
        # class create
        #
        # string property
        ar(TypeError, self.db.status.create, name=1)
        # invalid property name
        ar(KeyError, self.db.status.create, foo='foo')
        # key name clash
        ar(ValueError, self.db.status.create, name='unread')
        # invalid link index
        ar(IndexError, self.db.issue.create, title='foo', status='bar')
        # invalid link value
        ar(ValueError, self.db.issue.create, title='foo', status=1)
        # invalid multilink type
        ar(TypeError, self.db.issue.create, title='foo', status='1',
            nosy='hello')
        # invalid multilink index type
        ar(ValueError, self.db.issue.create, title='foo', status='1',
            nosy=[1])
        # invalid multilink index
        ar(IndexError, self.db.issue.create, title='foo', status='1',
            nosy=['10'])

        #
        # class get
        #
        # invalid node id
        ar(IndexError, self.db.status.get, '10', 'name')
        # invalid property name
        ar(KeyError, self.db.status.get, '2', 'foo')

        #
        # class set
        #
        # invalid node id
        ar(IndexError, self.db.issue.set, '1', name='foo')
        # invalid property name
        ar(KeyError, self.db.status.set, '1', foo='foo')
        # string property
        ar(TypeError, self.db.status.set, '1', name=1)
        # key name clash
        ar(ValueError, self.db.status.set, '2', name='unread')
        # set up a valid issue for me to work on
        self.db.issue.create(title="spam", status='1')
        # invalid link index
        ar(IndexError, self.db.issue.set, '1', title='foo', status='bar')
        # invalid link value
        ar(ValueError, self.db.issue.set, '1', title='foo', status=1)
        # invalid multilink type
        ar(TypeError, self.db.issue.set, '1', title='foo', status='1',
            nosy='hello')
        # invalid multilink index type
        ar(ValueError, self.db.issue.set, '1', title='foo', status='1',
            nosy=[1])
        # invalid multilink index
        ar(IndexError, self.db.issue.set, '1', title='foo', status='1',
            nosy=['10'])

    def testRetire(self):
        ''' test retiring a node
        '''
        pass


class ReadOnlyDBTestCase(unittest.TestCase):
    def setUp(self):
        class Database(anydbm.Database):
            pass
        # remove previous test, ignore errors
        if os.path.exists('_test_dir'):
            shutil.rmtree('_test_dir')
        os.mkdir('_test_dir')
        db = Database('_test_dir', 'test')
        setupSchema(db, 1)
        db.close()
        self.db = Database('_test_dir')
        setupSchema(self.db, 0)

    def testExceptions(self):
        # this tests the exceptions that should be raised
        ar = self.assertRaises

        # this tests the exceptions that should be raised
        ar(DatabaseError, self.db.status.create, name="foo")
        ar(DatabaseError, self.db.status.set, '1', name="foo")
        ar(DatabaseError, self.db.status.retire, '1')


def suite():
   db = unittest.makeSuite(DBTestCase, 'test')
   readonlydb = unittest.makeSuite(ReadOnlyDBTestCase, 'test')
   return unittest.TestSuite((db, readonlydb))


#
# $Log: test_db.py,v $
# Revision 1.6  2001/07/27 06:23:59  richard
# consistency
#
# Revision 1.5  2001/07/27 06:23:09  richard
# Added some new hyperdb tests to make sure we raise the right exceptions.
#
# Revision 1.4  2001/07/25 04:34:31  richard
# Added id and log to tests files...
#
#
