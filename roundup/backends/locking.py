#! /usr/bin/env python
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

# $Id: locking.py,v 1.6 2003/02/20 22:56:49 richard Exp $

'''This module provides a generic interface to acquire and release
exclusive access to a file.

It should work on Unix and Windows.
'''

# portalocker has a 0xffff0000 constant, and I don't need to know about it
# being positive in 2.4+ :)
try:
    x=FutureWarning
    import warnings
    warnings.filterwarnings("ignore",
        r'hex/oct constants > sys\.maxint .*', FutureWarning,
        'portalocker', 0)
    del x
except:
    pass

import portalocker

def acquire_lock(path, block=1):
    '''Acquire a lock for the given path
    '''
    import portalocker
    file = open(path, 'w')
    if block:
        portalocker.lock(file, portalocker.LOCK_EX)
    else:
        portalocker.lock(file, portalocker.LOCK_EX|portalocker.LOCK_NB)
    return file

def release_lock(file):
    '''Release our lock on the given path
    '''
    portalocker.unlock(file)
