# $Id: __init__.py,v 1.2 2001/07/28 06:43:02 richard Exp $

import unittest

import test_dates, test_schema, test_db, test_multipart

def go():
    suite = unittest.TestSuite((
        test_dates.suite(),
        test_schema.suite(),
        test_db.suite(),
        test_multipart.suite(),
    ))
    runner = unittest.TextTestRunner()
    runner.run(suite)

#
# $Log: __init__.py,v $
# Revision 1.2  2001/07/28 06:43:02  richard
# Multipart message class has the getPart method now. Added some tests for it.
#
# Revision 1.1  2001/07/27 06:55:07  richard
# moving tests -> test
#
# Revision 1.3  2001/07/25 04:34:31  richard
# Added id and log to tests files...
#
#
