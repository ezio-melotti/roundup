# $Id: init.py,v 1.5 2001/07/24 10:54:11 anthonybaxter Exp $

import os, shutil, sys

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
	print "making", dst
    except OSError, error:
        if error.errno != 17: raise
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

def init(instance, template, backend, adminpw):
    ''' initialise an instance using the named template
    '''
    # first, copy the template dir over
    import roundup.templatebuilder

    template_dir = os.path.split(__file__)[0]
    template_name = template
    template = os.path.join(template_dir, 'templates', template)
    copytree(template, instance)

    roundup.templatebuilder.installHtmlBase(template_name, instance)

    # now select database
    db = '''# WARNING: DO NOT EDIT THIS FILE!!!
from roundup.backends.back_%s import Database'''%backend
    open(os.path.join(instance, 'select_db.py'), 'w').write(db)

    # now import the instance and call its init
    path, instance = os.path.split(instance)
    sys.path.insert(0, path)
    instance = __import__(instance)
    instance.init(adminpw)

#
# $Log: init.py,v $
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
