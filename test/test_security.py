# Copyright (c) 2002 ekit.com Inc (http://www.ekit-inc.com/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# $Id: test_security.py,v 1.2 2002/07/26 08:27:00 richard Exp $

import os, unittest, shutil

from roundup.password import Password
from test_db import setupSchema, MyTestCase, config

class PermissionTest(MyTestCase):
    def setUp(self):
        from roundup.backends import anydbm
        # remove previous test, ignore errors
        if os.path.exists(config.DATABASE):
            shutil.rmtree(config.DATABASE)
        os.makedirs(config.DATABASE + '/files')
        self.db = anydbm.Database(config, 'test')
        setupSchema(self.db, 1, anydbm)

    def testInterfaceSecurity(self):
        ' test that the CGI and mailgw have initialised security OK '
        # TODO: some asserts

    def testInitialiseSecurity(self):
        ''' Create some Permissions and Roles on the security object

            This function is directly invoked by security.Security.__init__()
            as a part of the Security object instantiation.
        '''
        ei = self.db.security.addPermission(name="Edit", klass="issue",
                        description="User is allowed to edit issues")
        self.db.security.addPermissionToRole('User', ei)
        ai = self.db.security.addPermission(name="View", klass="issue",
                        description="User is allowed to access issues")
        self.db.security.addPermissionToRole('User', ai)

    def testGetPermission(self):
        self.db.security.getPermission('Edit')
        self.db.security.getPermission('View')
        self.assertRaises(ValueError, self.db.security.getPermission, 'x')
        self.assertRaises(ValueError, self.db.security.getPermission, 'Edit',
            'fubar')
        ei = self.db.security.addPermission(name="Edit", klass="issue",
                        description="User is allowed to edit issues")
        self.db.security.getPermission('Edit', 'issue')
        ai = self.db.security.addPermission(name="View", klass="issue",
                        description="User is allowed to access issues")
        self.db.security.getPermission('View', 'issue')

    def testDBinit(self):
        self.db.user.create(username="admin", roles='Admin')
        self.db.user.create(username="anonymous", roles='User')

    def testAccessControls(self):
        self.testDBinit()
        self.testInitialiseSecurity()

        # test class-level access
        userid = self.db.user.lookup('admin')
        self.assertEquals(self.db.security.hasPermission('Edit', userid,
            'issue'), 1)
        self.assertEquals(self.db.security.hasPermission('Edit', userid,
            'user'), 1)
        userid = self.db.user.lookup('anonymous')
        self.assertEquals(self.db.security.hasPermission('Edit', userid,
            'issue'), 1)
        self.assertEquals(self.db.security.hasPermission('Edit', userid,
            'user'), 0)

        # test node-level access
        issueid = self.db.issue.create(title='foo', assignedto='admin')
        userid = self.db.user.lookup('admin')
        self.assertEquals(self.db.security.hasNodePermission('issue',
            issueid, assignedto=userid), 1)
        self.assertEquals(self.db.security.hasNodePermission('issue',
            issueid, nosy=userid), 0)
        self.db.issue.set(issueid, nosy=[userid])
        self.assertEquals(self.db.security.hasNodePermission('issue',
            issueid, nosy=userid), 1)

def suite():
    return unittest.makeSuite(PermissionTest)


#
# $Log: test_security.py,v $
# Revision 1.2  2002/07/26 08:27:00  richard
# Very close now. The cgi and mailgw now use the new security API. The two
# templates have been migrated to that setup. Lots of unit tests. Still some
# issue in the web form for editing Roles assigned to users.
#
# Revision 1.1  2002/07/25 07:14:06  richard
# Bugger it. Here's the current shape of the new security implementation.
# Still to do:
#  . call the security funcs from cgi and mailgw
#  . change shipped templates to include correct initialisation and remove
#    the old config vars
# ... that seems like a lot. The bulk of the work has been done though. Honest :)
#
# Revision 1.1  2002/07/10 06:40:01  richard
# ehem, forgot to add
#
#
#
# vim: set filetype=python ts=4 sw=4 et si
