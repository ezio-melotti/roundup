#! /usr/bin/python
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
# $Id: roundup_mailgw.py,v 1.1 2002/01/29 19:53:08 jhermann Exp $

# python version check
from roundup import version_check

import sys, os, re, cStringIO

from roundup.mailgw import Message
from roundup.i18n import _

def do_pipe(handler):
    '''Read a message from standard input and pass it to the mail handler.
    '''
    handler.main(sys.stdin)
    return 0

def do_mailbox(handler, filename):
    '''Read a series of messages from the specified unix mailbox file and
    pass each to the mail handler.
    '''
    # open the spool file and lock it
    import fcntl, FCNTL
    f = open(filename, 'r+')
    fcntl.flock(f.fileno(), FCNTL.LOCK_EX)

    # handle and clear the mailbox
    try:
        from mailbox import UnixMailbox
        mailbox = UnixMailbox(f, factory=Message)
        # grab one message
        message = mailbox.next()
        while message:
            # call the instance mail handler
            handler.handle_Message(message)
            message = mailbox.next()
        # nuke the file contents
        os.ftruncate(f.fileno(), 0)
    except:
        import traceback
        traceback.print_exc()
        return 1
    fcntl.flock(f.fileno(), FCNTL.LOCK_UN)
    return 0

def do_pop(handler, server, user='', password=''):
    '''Read a series of messages from the specified POP server.
    '''
    import getpass, poplib, socket
    try:
        if not user:
            user = raw_input(_('User: '))
        if not password:
            password = getpass.getpass()
    except (KeyboardInterrupt, EOFError):
        # Ctrl C or D maybe also Ctrl Z under Windows.
        print "\nAborted by user."
        return 1

    # open a connection to the server and retrieve all messages
    try:
        server = poplib.POP3(server)
    except socket.error, message:
        print "POP server error:", message
        return 1
    server.user(user)
    server.pass_(password)
    numMessages = len(server.list()[1])
    for i in range(1, numMessages+1):
        # retr: returns 
        # [ pop response e.g. '+OK 459 octets',
        #   [ array of message lines ],
        #   number of octets ]
        lines = server.retr(i)[1]
        s = cStringIO.StringIO('\n'.join(lines))
        s.seek(0)
        handler.handle_Message(Message(s))
        # delete the message
        server.dele(i)

    # quit the server to commit changes.
    server.quit()
    return 0

def usage(args, message=None):
    if message is not None:
        print message
    print _('Usage: %(program)s <instance home> [source spec]')%{'program': args[0]}
    print _('''
The roundup mail gateway may be called in one of two ways:
 . with an instance home as the only argument,
 . with both an instance home and a mail spool file, or
 . with both an instance home and a pop server account.

PIPE:
 In the first case, the mail gateway reads a single message from the
 standard input and submits the message to the roundup.mailgw module.

UNIX mailbox:
 In the second case, the gateway reads all messages from the mail spool
 file and submits each in turn to the roundup.mailgw module. The file is
 emptied once all messages have been successfully handled. The file is
 specified as:
   mailbox /path/to/mailbox

POP:
 In the third case, the gateway reads all messages from the POP server
 specified and submits each in turn to the roundup.mailgw module. The
 server is specified as:
    pop username:password@server
 The username and password may be omitted:
    pop username@server
    pop server
 are both valid. The username and/or password will be prompted for if
 not supplied on the command-line.
''')
    return 1

def main(args):
    '''Handle the arguments to the program and initialise environment.
    '''
    # figure the instance home
    if len(args) > 1:
        instance_home = args[1]
    else:
        instance_home = os.environ.get('ROUNDUP_INSTANCE', '')
    if not instance_home:
        return usage(args)

    # get the instance
    import roundup.instance
    instance = roundup.instance.open(instance_home)

    # get a mail handler
    db = instance.open('admin')
    handler = instance.MailGW(instance, db)

    # if there's no more arguments, read a single message from stdin
    if len(args) == 2:
        return do_pipe(handler)

    # otherwise, figure what sort of mail source to handle
    if len(args) < 4:
        return usage(args, _('Error: not enough source specification information'))
    source, specification = args[2:]
    if source == 'mailbox':
        return do_mailbox(handler, specification)
    elif source == 'pop':
        m = re.match(r'((?P<user>[^:]+)(:(?P<pass>.+))?@)?(?P<server>.+)',
            specification)
        if m:
            return do_pop(handler, m.group('server'), m.group('user'),
                m.group('pass'))
        return usage(args, _('Error: pop specification not valid'))

    return usage(args, _('Error: The source must be either "mailbox" or "pop"'))

# call main
if __name__ == '__main__':
    sys.exit(main(sys.argv))

#
# $Log: roundup_mailgw.py,v $
# Revision 1.1  2002/01/29 19:53:08  jhermann
# Moved scripts from top-level dir to roundup.scripts subpackage
#
# Revision 1.21  2002/01/11 07:02:29  grubert
# put an exception around: do_pop user and password entry to catch ctrl-c/d.
#
# Revision 1.20  2002/01/07 10:43:48  richard
# #500329 ] exception on server not reachable-patch
#
# Revision 1.19  2002/01/05 02:19:03  richard
# i18n'ification
#
# Revision 1.18  2001/12/13 00:20:01  richard
#  . Centralised the python version check code, bumped version to 2.1.1 (really
#    needs to be 2.1.2, but that isn't released yet :)
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
# Revision 1.16  2001/11/30 18:23:55  jhermann
# Cleaned up strange import (less pollution, too)
#
# Revision 1.15  2001/11/30 13:16:37  rochecompaan
# Fixed bug. Mail gateway was not using the extended Message class
# resulting in failed submissions when mails were processed from a Unix
# mailbox
#
# Revision 1.14  2001/11/13 21:44:44  richard
#  . re-open the database as the author in mail handling
#
# Revision 1.13  2001/11/09 01:05:55  richard
# Fixed bug #479511 ] mailgw to pop once engelbert gruber tested the POP
# gateway.
#
# Revision 1.12  2001/11/08 05:16:55  richard
# Rolled roundup-popgw into roundup-mailgw. Cleaned mailgw up significantly,
# tested unix mailbox some more. POP still untested.
#
# Revision 1.11  2001/11/07 05:32:58  richard
# More roundup-mailgw usage help.
#
# Revision 1.10  2001/11/07 05:30:11  richard
# Nicer usage message.
#
# Revision 1.9  2001/11/07 05:29:26  richard
# Modified roundup-mailgw so it can read e-mails from a local mail spool
# file. Truncates the spool file after parsing.
# Fixed a couple of small bugs introduced in roundup.mailgw when I started
# the popgw.
#
# Revision 1.8  2001/11/01 22:04:37  richard
# Started work on supporting a pop3-fetching server
# Fixed bugs:
#  . bug #477104 ] HTML tag error in roundup-server
#  . bug #477107 ] HTTP header problem
#
# Revision 1.7  2001/08/07 00:24:42  richard
# stupid typo
#
# Revision 1.6  2001/08/07 00:15:51  richard
# Added the copyright/license notice to (nearly) all files at request of
# Bizar Software.
#
# Revision 1.5  2001/08/05 07:44:25  richard
# Instances are now opened by a special function that generates a unique
# module name for the instances on import time.
#
# Revision 1.4  2001/08/03 01:28:33  richard
# Used the much nicer load_package, pointed out by Steve Majewski.
#
# Revision 1.3  2001/08/03 00:59:34  richard
# Instance import now imports the instance using imp.load_module so that
# we can have instance homes of "roundup" or other existing python package
# names.
#
# Revision 1.2  2001/07/29 07:01:39  richard
# Added vim command to all source so that we don't get no steenkin' tabs :)
#
# Revision 1.1  2001/07/23 03:46:48  richard
# moving the bin files to facilitate out-of-the-boxness
#
# Revision 1.1  2001/07/22 11:15:45  richard
# More Grande Splite stuff
#
#
# vim: set filetype=python ts=4 sw=4 et si
