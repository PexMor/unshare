#!/usr/bin/env python2

import ctypes
import os
from multiprocessing import Process
from FS import *
from SCHED import *

libc = ctypes.CDLL(None)

# type safety of the function arg types so we make sure proper conversions are done
# to check you can use: strace -fe "mount,pivot_root,unshare" -- ./your-python.py
libc.pivot_root.argtypes = [ctypes.c_char_p,ctypes.c_char_p]
libc.mount.argtypes = [ctypes.c_char_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_ulong,ctypes.c_void_p]
libc.unshare.argtypes = [ctypes.c_int]

get_errno_loc = libc.__errno_location
get_errno_loc.restype.restype = ctypes.POINTER(ctypes.c_int)

pivot_dir = '/tmp/pivot/rootfs'

def unshare(flags):
    """Disassociate part of execution context
    The parts are identified by parameter flags which is a bitmap.
    For constant names see "man 2 unshare"
    This is a wrapper for libc function which actually wraps syscall
    a kernel function see "man 2 syscalls"
    """
    print(":: Call unshare function")
    rc = libc.unshare(flags)
    if rc == -1:
        raise Exception(os.strerror(get_errno_loc()[0]))

def mount(special_file, target, fs_type, flags, data):
    """Mount or remount a filesystem
    A libc wrapper linked to actual syscall.
    """
    print(":: Call mount function")
    rc = libc.mount(
        ctypes.c_char_p(special_file if special_file is None else special_file.encode("utf-8")),
        ctypes.c_char_p(target if target is None else target.encode("utf-8")),
        ctypes.c_char_p(fs_type if fs_type is None else fs_type.encode("utf-8")),
        flags,
        ctypes.c_void_p(data))
    if rc == -1:
        raise Exception(os.strerror(get_errno_loc()[0]))

def pivot_root(newroot,putold):
    """Change the current filesystem root to newroot and put the old root into putold directory.
    This function rebases the filesystem so it gets isolated inside a subtree.
    A libc wrapper. The putold has to be a directory within the newroot.
    """
    print(":: Call pivot_root function")
    rc = libc.pivot_root(ctypes.c_char_p(newroot.encode("utf-8")),ctypes.c_char_p(putold.encode("utf-8")))
    if rc == -1:
        raise Exception(os.strerror(get_errno_loc()[0]))

def unshare_user():
    """Create new uid namespace with uid mapping setting current user a superuser.
    Though the user becomes a root only inside his process execution context.
    From outside view the user is actually mapped to actual uid, usualy 1000.
    This is in case you are the 1st user on your computer.
    """
    uidmapfile = '/proc/self/uid_map'
    # order of operations is important as os.getuid() gets the actual value
    # it changes after the unshare(CLONE_NEWUSER) to int16(-1) ~ 65534 (nobody)
    # hint: getent passwd 65535
    uidmap = "0 %d 1" % os.getuid()
    print("My uid = %d my actuall uid (might be 1000)" % os.getuid())
    unshare(CLONE_NEWUSER)
    print("Writing uidmap = '%s' to '%s'" % (uidmap, uidmapfile))
    with open(uidmapfile,'w') as file_:
        file_.write(uidmap)
    print("My uid = %d which supposed to be 0 ~ super user aka root" % os.getuid())


def mount_proc():
    """Mount the /proc special filesystem
    It expects that you already have moved into own root fs and want to map
    your restricted set of processes as convenient filesystem view.
    """
    if not os.path.exists('/proc'):
        os.makedirs('/proc')
    mount('proc','/proc','proc', MS_NODEV ^ MS_NOEXEC ^ MS_NOSUID, None)


def sh():
    """Start a shell /bin/sh which might be mapped to actuall bash, zsh or other
    """
    os.execve('/bin/sh', ['/bin/sh'], { 'PATH': os.getenv('PATH')})

def cmd():
    """Execute a shell in root fs pivoted to a new root
    """
    base = (pivot_dir)
    oldroot = os.path.join(base,'host')
    if not os.path.exists(oldroot):
        os.makedirs(oldroot)
    # issue with root fs also described at:
    # https://lists.freedesktop.org/archives/systemd-devel/2014-May/019193.html
    print("")
    mount('none' , '/' , None, MS_REC ^ MS_PRIVATE, None)
    mount(base, base, None, MS_REC ^ MS_BIND, None)
    os.chdir(base)
    print("pivot root")
    pivot_root(".","host")
    print("mount proc")
    mount_proc()
    sh()

def contit():
    unshare_user()
    unshare(CLONE_NEWNET ^ CLONE_NEWPID ^ CLONE_NEWNS)
    p = Process(target=cmd)
    p.start()

contit()
