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
# $Id: __init__.py,v 1.11 2002/09/11 21:39:17 richard Exp $

__doc__ = '''
This is a simple-to-use and -install issue-tracking system with
command-line, web and e-mail interfaces.

Roundup manages a number of issues (with properties such as
"description", "priority", and so on) and provides the ability to (a) submit
new issues, (b) find and edit existing issues, and (c) discuss issues with
other participants. The system will facilitate communication among the
participants by managing discussions and notifying interested parties when
issues are edited. 

Roundup's structure is that of a cake:

 _________________________________________________________________________
|  E-mail Client   |   Web Browser   |   Detector Scripts   |    Shell    |
|------------------+-----------------+----------------------+-------------|
|   E-mail User    |    Web User     |      Detector        |   Command   | 
|-------------------------------------------------------------------------|
|                         Roundup Database Layer                          |
|-------------------------------------------------------------------------|
|                          Hyperdatabase Layer                            |
|-------------------------------------------------------------------------|
|                             Storage Layer                               |
 -------------------------------------------------------------------------

The first layer represents the users (chocolate).
The second layer is the Roundup interface to the users (vanilla).
The third and fourth layers are the internal Roundup database storage
  mechanisms (strawberry).
The final, lowest layer is the underlying database storage (rum).

These are implemented in the code in the following manner:
  E-mail User: roundup-mailgw and roundup.mailgw
     Web User: cgi-bin/roundup.cgi or roundup-server over
               roundup.cgi_client, roundup.cgitb and roundup.htmltemplate
     Detector: roundup.roundupdb and templates/<template>/detectors
      Command: roundup-admin
   Roundup DB: roundup.roundupdb
     Hyper DB: roundup.hyperdb, roundup.date
      Storage: roundup.backends.*

Additionally, there is a directory of unit tests in "test".

For more information, see the original overview and specification documents
written by Ka-Ping Yee in the "doc" directory. If nothing else, it has a
much prettier cake :)
'''

__version__ = '0.5.0b1'

# vim: set filetype=python ts=4 sw=4 et si
