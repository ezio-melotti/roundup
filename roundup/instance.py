#
# Copyright (c) 2001 Bizar Software Pty Ltd (http://www.bizarsoftware.com.au/)
# This module is free software, and you may redistribute it and/or modify
# under the same terms as Python, so long as this copyright message and
# disclaimer are retained in their original form.
#
# IN NO EVENT SHALL BIZAR SOFTWARE PTY LTD BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING
# OUT OF THE USE OF THIS CODE, EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# BIZAR SOFTWARE PTY LTD SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE.  THE CODE PROVIDED HEREUNDER IS ON AN "AS IS"
# BASIS, AND THERE IS NO OBLIGATION WHATSOEVER TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#
# $Id: instance.py,v 1.27 2004/11/02 10:00:36 a1s Exp $

'''Tracker handling (open tracker).

Backwards compatibility for the old-style "imported" trackers.
'''
__docformat__ = 'restructuredtext'

import os
from roundup import configuration, mailgw, rlog
from roundup import hyperdb, backends
from roundup.cgi import client, templating

class Vars:
    def __init__(self, vars):
        self.__dict__.update(vars)

class Tracker:
    def __init__(self, tracker_home, optimize=0):
        """New-style tracker instance constructor

        Parameters:
            tracker_home:
                tracker home directory
            optimize:
                if set, precompile html templates

        """
        self.tracker_home = tracker_home
        self.optimize = optimize
        self.config = configuration.CoreConfig(tracker_home)
        self.cgi_actions = {}
        self.templating_utils = {}
        self.load_interfaces()
        self.templates = templating.Templates(self.config["TEMPLATES"])
        if self.optimize:
            self.templates.precompileTemplates()

    def get_backend_name(self):
        o = __builtins__['open']
        f = o(os.path.join(self.tracker_home, 'db', 'backend_name'))
        name = f.readline().strip()
        f.close()
        return name

    def get_backend(self):
        name = self.get_backend_name()
        return getattr(backends, name)

    def open(self, name=None):
        backend = self.get_backend()
        vars = {
            'Class': backend.Class,
            'FileClass': backend.FileClass,
            'IssueClass': backend.IssueClass,
            'String': hyperdb.String,
            'Password': hyperdb.Password,
            'Date': hyperdb.Date,
            'Link': hyperdb.Link,
            'Multilink': hyperdb.Multilink,
            'Interval': hyperdb.Interval,
            'Boolean': hyperdb.Boolean,
            'Number': hyperdb.Number,
            'db': backend.Database(self.config, name)
        }
        self._load_python('schema.py', vars)
        db = vars['db']

        self.load_extensions(db, 'detectors')
        self.load_extensions(self, 'extensions')

        db.post_init()
        return db

    def load_interfaces(self):
        """load interfaces.py (if any), initialize Client and MailGW attrs"""
        vars = {}
        if os.path.isfile(os.path.join(self.tracker_home, 'interfaces.py')):
            self._load_python('interfaces.py', vars)
        self.Client = vars.get('Client', client.Client)
        self.MailGW = vars.get('MailGW', mailgw.MailGW)

    def load_extensions(self, parent, dirname):
        dirpath = os.path.join(self.tracker_home, dirname)
        if os.path.isdir(dirpath):
            for name in os.listdir(dirpath):
                if not name.endswith('.py'):
                    continue
                vars = {}
                self._load_python(os.path.join(dirname, name), vars)
                vars['init'](parent)

    def init(self, adminpw):
        db = self.open('admin')
        self._load_python('initial_data.py', {'db': db, 'adminpw': adminpw,
            'admin_email': self.config['ADMIN_EMAIL']})
        db.commit()
        db.close()

    def exists(self):
        backend = self.get_backend()
        return backend.db_exists(self.config)

    def nuke(self):
        backend = self.get_backend()
        backend.db_nuke(self.config)

    def _load_python(self, file, vars):
        file = os.path.join(self.tracker_home, file)
        execfile(file, vars)
        return vars

    def registerAction(self, name, action):
        self.cgi_actions[name] = action

    def registerUtil(self, name, function):
        self.templating_utils[name] = function

class TrackerError(Exception):
    pass


class OldStyleTrackers:
    def __init__(self):
        self.number = 0
        self.trackers = {}

    def open(self, tracker_home, optimize=0):
        """Open the tracker.

        Parameters:
            tracker_home:
                tracker home directory
            optimize:
                if set, precompile html templates

        Raise ValueError if the tracker home doesn't exist.

        """
        import imp
        # sanity check existence of tracker home
        if not os.path.exists(tracker_home):
            raise ValueError, 'no such directory: "%s"'%tracker_home

        # sanity check tracker home contents
        for reqd in 'config dbinit select_db interfaces'.split():
            if not os.path.exists(os.path.join(tracker_home, '%s.py'%reqd)):
                raise TrackerError, 'File "%s.py" missing from tracker '\
                    'home "%s"'%(reqd, tracker_home)

        if self.trackers.has_key(tracker_home):
            return imp.load_package(self.trackers[tracker_home],
                tracker_home)
        self.number = self.number + 1
        modname = '_roundup_tracker_%s'%self.number
        self.trackers[tracker_home] = modname

        # load the tracker
        tracker = imp.load_package(modname, tracker_home)

        # ensure the tracker has all the required bits
        for required in 'open init Client MailGW'.split():
            if not hasattr(tracker, required):
                raise TrackerError, \
                    'Required tracker attribute "%s" missing'%required

        # load and apply the config
        tracker.config = configuration.CoreConfig(tracker_home)
        # FIXME! dbinit does "import config".
        #   What would be the upgrade plan for existing trackers?
        tracker.dbinit.config = tracker.config

        tracker.optimize = optimize
        tracker.templates = templating.Templates(tracker.config["TEMPLATES"])
        if optimize:
            tracker.templates.precompileTemplates()

        return tracker

OldStyleTrackers = OldStyleTrackers()
def open(tracker_home, optimize=0):
    if os.path.exists(os.path.join(tracker_home, 'dbinit.py')):
        # user should upgrade...
        return OldStyleTrackers.open(tracker_home, optimize=optimize)

    return Tracker(tracker_home, optimize=optimize)

# vim: set filetype=python sts=4 sw=4 et si :
