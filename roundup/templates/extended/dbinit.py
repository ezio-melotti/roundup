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
# $Id: dbinit.py,v 1.24 2002/07/26 08:27:00 richard Exp $

import os

import instance_config
from select_db import Database, Class, FileClass, IssueClass

def open(name=None):
    ''' as from the roundupdb method openDB 
    ''' 
    from roundup.hyperdb import String, Password, Date, Link, Multilink

    # open the database
    db = Database(instance_config, name)

    #
    # Now initialise the schema. Must do this each time the database is
    # opened.
    #

    # Class automatically gets these properties:
    #   creation = Date()
    #   activity = Date()
    #   creator = Link('user')
    pri = Class(db, "priority", 
                    name=String(), order=String())
    pri.setkey("name")

    stat = Class(db, "status", 
                    name=String(), order=String())
    stat.setkey("name")

    keywords = Class(db, "keyword", 
                    name=String())
    keywords.setkey("name")

    user = Class(db, "user", 
                    username=String(),   password=Password(),
                    address=String(),    realname=String(), 
                    phone=String(),      organisation=String(),
                    alternate_addresses=String(),
                    queries=Multilink('query'), roles=String())
    user.setkey("username")

    # FileClass automatically gets these properties:
    #   content = String()    [saved to disk in <instance home>/db/files/]
    #   (it also gets the Class properties creation, activity and creator)
    msg = FileClass(db, "msg", 
                    author=Link("user"), recipients=Multilink("user"), 
                    date=Date(),         summary=String(), 
                    files=Multilink("file"),
                    messageid=String(),  inreplyto=String())

    file = FileClass(db, "file", 
                    name=String(),       type=String())

    # bugs and support calls etc
    rate = Class(db, "rate", 
                    name=String(),       order=String())
    rate.setkey("name")

    source = Class(db, "source", 
                    name=String(),       order=String())
    source.setkey("name")

    platform = Class(db, "platform", 
                    name=String(),       order=String())
    platform.setkey("name")

    product = Class(db, "product", 
                    name=String(),       order=String())
    product.setkey("name")

    timelog = Class(db, "timelog", 
                    date=Date(),         time=String(),
                    performedby=Link("user"), description=String())

    # IssueClass automatically gets these properties:
    #   title = String()
    #   messages = Multilink("msg")
    #   files = Multilink("file")
    #   nosy = Multilink("user")
    #   superseder = Multilink("issue")
    #   (it also gets the Class properties creation, activity and creator)
    support = IssueClass(db, "support", 
                    assignedto=Link("user"), status=Link("status"),
                    rate=Link("rate"), source=Link("source"),
                    product=Link("product"), platform=Multilink("platform"),
                    version=String(), timelog=Multilink("timelog"),
                    customername=String())

    issue = IssueClass(db, "issue", 
                    assignedto=Link("user"), priority=Link("priority"), 
                    status=Link("status"), product=Link("product"), 
                    platform=Multilink("platform"), version=String(),
                    targetversion=String(), supportcall=Multilink("support"))

    #
    # SECURITY SETTINGS
    #
    # new permissions for this schema
    for cl in 'issue', 'support', 'file', 'msg':
        db.security.addPermission(name="Edit", klass=cl,
            description="User is allowed to edit "+cl)
        db.security.addPermission(name="View", klass=cl,
            description="User is allowed to access "+cl)

    # Assign the appropriate permissions to the anonymous user's Anonymous
    # Role. Choices here are:
    # - Allow anonymous users to register through the web
    p = db.security.getPermission('Web Registration')
    db.security.addPermissionToRole('Anonymous', p)
    # - Allow anonymous (new) users to register through the email gateway
    p = db.security.getPermission('Email Registration')
    db.security.addPermissionToRole('Anonymous', p)
    # - Allow anonymous users access to the "issue" class of data
    #   Note: this also grants access to related information like files,
    #         messages, statuses etc that are linked to issues
    #p = db.security.getPermission('View', 'issue')
    #db.security.addPermissionToRole('Anonymous', p)
    # - Allow anonymous users access to edit the "issue" class of data
    #   Note: this also grants access to create related information like
    #         files and messages etc that are linked to issues
    #p = db.security.getPermission('Edit', 'issue')
    #db.security.addPermissionToRole('Anonymous', p)

    # Assign the access and edit permissions for issue, file and message
    # to regular users now
    for cl in 'issue', 'support', 'file', 'msg':
        p = db.security.getPermission('View', cl)
        db.security.addPermissionToRole('User', p)
        p = db.security.getPermission('Edit', cl)
        db.security.addPermissionToRole('User', p)

    import detectors
    detectors.init(db)

    # schema is set up - run any post-initialisation
    db.post_init()
    return db
 
def init(adminpw): 
    ''' as from the roundupdb method initDB 
 
    Open the new database, and add new nodes - used for initialisation. You
    can edit this before running the "roundup-admin initialise" command to
    change the initial database entries.
    ''' 
    dbdir = os.path.join(instance_config.DATABASE, 'files')
    if not os.path.isdir(dbdir):
        os.makedirs(dbdir)

    db = open("admin")
    db.clear()

    pri = db.getclass('priority')
    pri.create(name="fatal-bug", order="1")
    pri.create(name="bug", order="2")
    pri.create(name="usability", order="3")
    pri.create(name="feature", order="4")

    stat = db.getclass('status')
    stat.create(name="unread", order="1")
    stat.create(name="deferred", order="2")
    stat.create(name="chatting", order="3")
    stat.create(name="need-eg", order="4")
    stat.create(name="in-progress", order="5")
    stat.create(name="testing", order="6")
    stat.create(name="done-cbb", order="7")
    stat.create(name="resolved", order="8")

    rate = db.getclass("rate")
    rate.create(name='basic', order="1")
    rate.create(name='premium', order="2")
    rate.create(name='internal', order="3")

    source = db.getclass("source")
    source.create(name='phone', order="1")
    source.create(name='e-mail', order="2")
    source.create(name='internal', order="3")
    source.create(name='internal-qa', order="4")

    platform = db.getclass("platform")
    platform.create(name='linux', order="1")
    platform.create(name='windows', order="2")
    platform.create(name='mac', order="3")

    product = db.getclass("product")
    product.create(name='Bizar Shop', order="1")
    product.create(name='Bizar Shop Developer', order="2")
    product.create(name='Bizar Shop Manual', order="3")
    product.create(name='Bizar Shop Developer Manual', order="4")

    user = db.getclass('user')
    user.create(username="admin", password=adminpw, 
        address=instance_config.ADMIN_EMAIL, roles="Admin")
    user.create(username="anonymous", roles='Anonymous')

    db.commit()

#
# $Log: dbinit.py,v $
# Revision 1.24  2002/07/26 08:27:00  richard
# Very close now. The cgi and mailgw now use the new security API. The two
# templates have been migrated to that setup. Lots of unit tests. Still some
# issue in the web form for editing Roles assigned to users.
#
# Revision 1.23  2002/07/14 02:05:54  richard
# . all storage-specific code (ie. backend) is now implemented by the backends
#
# Revision 1.22  2002/07/09 03:02:53  richard
# More indexer work:
# - all String properties may now be indexed too. Currently there's a bit of
#   "issue" specific code in the actual searching which needs to be
#   addressed. In a nutshell:
#   + pass 'indexme="yes"' as a String() property initialisation arg, eg:
#         file = FileClass(db, "file", name=String(), type=String(),
#             comment=String(indexme="yes"))
#   + the comment will then be indexed and be searchable, with the results
#     related back to the issue that the file is linked to
# - as a result of this work, the FileClass has a default MIME type that may
#   be overridden in a subclass, or by the use of a "type" property as is
#   done in the default templates.
# - the regeneration of the indexes (if necessary) is done once the schema is
#   set up in the dbinit.
#
# Revision 1.21  2002/05/24 04:03:23  richard
# Added commentage to the dbinit files to help people with their
# customisation.
#
# Revision 1.20  2002/02/15 07:08:44  richard
#  . Alternate email addresses are now available for users. See the MIGRATION
#    file for info on how to activate the feature.
#
# Revision 1.19  2002/01/14 02:20:15  richard
#  . changed all config accesses so they access either the instance or the
#    config attriubute on the db. This means that all config is obtained from
#    instance_config instead of the mish-mash of classes. This will make
#    switching to a ConfigParser setup easier too, I hope.
#
# At a minimum, this makes migration a _little_ easier (a lot easier in the
# 0.5.0 switch, I hope!)
#
# Revision 1.18  2002/01/02 02:31:38  richard
# Sorry for the huge checkin message - I was only intending to implement #496356
# but I found a number of places where things had been broken by transactions:
#  . modified ROUNDUPDBSENDMAILDEBUG to be SENDMAILDEBUG and hold a filename
#    for _all_ roundup-generated smtp messages to be sent to.
#  . the transaction cache had broken the roundupdb.Class set() reactors
#  . newly-created author users in the mailgw weren't being committed to the db
#
# Stuff that made it into CHANGES.txt (ie. the stuff I was actually working
# on when I found that stuff :):
#  . #496356 ] Use threading in messages
#  . detectors were being registered multiple times
#  . added tests for mailgw
#  . much better attaching of erroneous messages in the mail gateway
#
# Revision 1.17  2001/12/02 05:06:16  richard
# . We now use weakrefs in the Classes to keep the database reference, so
#   the close() method on the database is no longer needed.
#   I bumped the minimum python requirement up to 2.1 accordingly.
# . #487480 ] roundup-server
# . #487476 ] INSTALL.txt
#
# I also cleaned up the change message / post-edit stuff in the cgi client.
# There's now a clearly marked "TODO: append the change note" where I believe
# the change note should be added there. The "changes" list will obviously
# have to be modified to be a dict of the changes, or somesuch.
#
# More testing needed.
#
# Revision 1.16  2001/12/01 07:17:50  richard
# . We now have basic transaction support! Information is only written to
#   the database when the commit() method is called. Only the anydbm
#   backend is modified in this way - neither of the bsddb backends have been.
#   The mail, admin and cgi interfaces all use commit (except the admin tool
#   doesn't have a commit command, so interactive users can't commit...)
# . Fixed login/registration forwarding the user to the right page (or not,
#   on a failure)
#
# Revision 1.15  2001/11/26 22:55:56  richard
# Feature:
#  . Added INSTANCE_NAME to configuration - used in web and email to identify
#    the instance.
#  . Added EMAIL_SIGNATURE_POSITION to indicate where to place the roundup
#    signature info in e-mails.
#  . Some more flexibility in the mail gateway and more error handling.
#  . Login now takes you to the page you back to the were denied access to.
#
# Fixed:
#  . Lots of bugs, thanks Roch� and others on the devel mailing list!
#
# Revision 1.14  2001/11/21 02:34:18  richard
# Added a target version field to the extended issue schema
#
# Revision 1.13  2001/10/30 00:54:45  richard
# Features:
#  . #467129 ] Lossage when username=e-mail-address
#  . #473123 ] Change message generation for author
#  . MailGW now moves 'resolved' to 'chatting' on receiving e-mail for an issue.
#
# Revision 1.12  2001/10/09 07:25:59  richard
# Added the Password property type. See "pydoc roundup.password" for
# implementation details. Have updated some of the documentation too.
#
# Revision 1.11  2001/08/07 00:24:43  richard
# stupid typo
#
# Revision 1.10  2001/08/07 00:15:51  richard
# Added the copyright/license notice to (nearly) all files at request of
# Bizar Software.
#
# Revision 1.9  2001/08/02 06:38:17  richard
# Roundupdb now appends "mailing list" information to its messages which
# include the e-mail address and web interface address. Templates may
# override this in their db classes to include specific information (support
# instructions, etc).
#
# Revision 1.8  2001/07/30 01:26:59  richard
# Big changes:
#  . split off the support priority into its own class
#  . added "new support, new user" to the page head
#  . fixed the display options for the heading links
#
# Revision 1.7  2001/07/29 07:01:39  richard
# Added vim command to all source so that we don't get no steenkin' tabs :)
#
# Revision 1.6  2001/07/25 01:23:07  richard
# Added the Roundup spec to the new documentation directory.
#
# Revision 1.5  2001/07/23 23:20:35  richard
# forgot to remove the interfaces from the dbinit module ;)
#
# Revision 1.4  2001/07/23 08:45:28  richard
# ok, so now "./roundup-admin init" will ask questions in an attempt to get a
# workable instance_home set up :)
# _and_ anydbm has had its first test :)
#
# Revision 1.3  2001/07/23 07:14:41  richard
# Moved the database backends off into backends.
#
# Revision 1.2  2001/07/23 06:25:50  richard
# relfected the move to roundup/backends
#
# Revision 1.1  2001/07/23 04:33:21  anthonybaxter
# split __init__.py into 2. dbinit and instance_config.
#
# Revision 1.1  2001/07/23 03:50:46  anthonybaxter
# moved templates to proper location
#
# Revision 1.2  2001/07/22 12:09:32  richard
# Final commit of Grande Splite
#
#
# vim: set filetype=python ts=4 sw=4 et si

