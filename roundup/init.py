# $Id: init.py,v 1.9 2001/08/03 00:59:34 richard Exp $

import os, shutil, sys, errno, imp

def copytree(src, dst, symlinks=0):
    """Recursively copy a directory tree using copy2().

    The destination directory os allowed to exist.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    XXX copied from shutil.py in std lib

    """
    names = os.listdir(src)
    try:
        os.mkdir(dst)
    except OSError, error:
        if error.errno != errno.EEXIST: raise
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if symlinks and os.path.islink(srcname):
            linkto = os.readlink(srcname)
            os.symlink(linkto, dstname)
        elif os.path.isdir(srcname):
            copytree(srcname, dstname, symlinks)
        else:
            shutil.copy2(srcname, dstname)

def init(instance_home, template, backend, adminpw):
    ''' initialise an instance using the named template
    '''
    # first, copy the template dir over
    import roundup.templatebuilder

    template_dir = os.path.split(__file__)[0]
    template_name = template
    template = os.path.join(template_dir, 'templates', template)
    copytree(template, instance_home)

    roundup.templatebuilder.installHtmlBase(template_name, instance_home)

    # now select database
    db = '''# WARNING: DO NOT EDIT THIS FILE!!!
from roundup.backends.back_%s import Database'''%backend
    open(os.path.join(instance_home, 'select_db.py'), 'w').write(db)

    # now import the instance and call its init
    instance = imp.load_module('instance', None, instance_home, ('', '', 5))
    instance.init(adminpw)

#
# $Log: init.py,v $
# Revision 1.9  2001/08/03 00:59:34  richard
# Instance import now imports the instance using imp.load_module so that
# we can have instance homes of "roundup" or other existing python package
# names.
#
# Revision 1.8  2001/07/29 07:01:39  richard
# Added vim command to all source so that we don't get no steenkin' tabs :)
#
# Revision 1.7  2001/07/28 07:59:53  richard
# Replaced errno integers with their module values.
# De-tabbed templatebuilder.py
#
# Revision 1.6  2001/07/24 11:18:25  anthonybaxter
# oops. left a print in
#
# Revision 1.5  2001/07/24 10:54:11  anthonybaxter
# oops. Html.
#
# Revision 1.4  2001/07/24 10:46:22  anthonybaxter
# Added templatebuilder module. two functions - one to pack up the html base,
# one to unpack it. Packed up the two standard templates into htmlbases.
# Modified __init__ to install them.
#
# __init__.py magic was needed for the rather high levels of wierd import magic.
# Reducing level of import magic == (good, future)
#
# Revision 1.3  2001/07/23 08:45:28  richard
# ok, so now "./roundup-admin init" will ask questions in an attempt to get a
# workable instance_home set up :)
# _and_ anydbm has had its first test :)
#
# Revision 1.2  2001/07/22 12:09:32  richard
# Final commit of Grande Splite
#
#
# vim: set filetype=python ts=4 sw=4 et si
