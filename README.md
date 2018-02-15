# Unshare
The beauty and the beast (story of python and unshare)

This repo is inteded to put together some information from past [Prague Containers meetup](https://www.meetup.com/Prague-Containers-Meetup/events/247182043/). Where David Bečvařík [@Github](https://github.com/dbecvarik) has interactively demoed how to in a few calls isolate linux process by the means of linux namespaces.

[His original Gist](https://gist.github.com/dbecvarik/33d7aeff44d6839fada7c95a98450f1e)

Once upon the time there was linux namespaces, living in ```01-syscall.py```.

```python
import ctypes
from FS import *
from SCHED import *

libc = ctypes.CDLL(None)
libc.unshare.argtypes = [ctypes.c_int]

get_errno_loc = libc.__errno_location
get_errno_loc.restype.restype = ctypes.POINTER(ctypes.c_int)

def unshare(flags):
    rc = libc.unshare(flags)
    if rc == -1:
        raise Exception(os.strerror(get_errno_loc()[0]))

def unshare_user():
    uidmapfile = '/proc/self/uid_map'
    uidmap = "0 %d 1" % os.getuid()
    print("My uid = %d my actuall uid (might be 1000)" % os.getuid())
    unshare(CLONE_NEWUSER)
    print("Writing uidmap = '%s' to '%s'" % (uidmap, uidmapfile))
    with open(uidmapfile,'w') as file_:
        file_.write(uidmap)
    print("My uid = %d which supposed to be 0 ~ super user aka root" % os.getuid())

unshare_user()
# here I am superuser in my little box
```

The code above is small and initial part of the namespace separation, for more read the [01-syscall.py](01-syscall.py) which does more magic and at the end starts the shell.

## Python ctypes

Ctypes is a c-style call conventions to python call convetions bridge. Is is capable of many magic things, among other creating mutable string buffer (compare to python imutable string). It has slightly different behavior in python 2 and 3 series. Thus be carefull with code. The code here should run on both pythons.

[Access errno in ctypes](https://stackoverflow.com/questions/661017/access-to-errno-from-python)

## Some handy man pages

[man 1 unshare](https://linux.die.net/man/1/unshare) - The shell command to invoke libc/syscall to separate part of execution context from parent process.

```bash
# has to be run as root (or CLONE_NEWUSER and root mapped)
sudo unshare -m -u -i -n -p -f --user --mount-proc bash
```

[man 1 nsenter](https://linux.die.net/man/1/nsenter) - The shell command to enter into another process namespace (derived from its PID). Access controll restrictions apply.

[man 1 chroot](https://linux.die.net/man/1/chroot) - Moves the root of the filesystem into some directory. It is not the same as jail or pivot_root. It is rather complementary as ```chroot .``` is trick to fix working directories after ```pivot_root```

[man 1 strace](https://linux.die.net/man/1/strace) - Your friend when debugging:

```bash
strace -fe "mount,pivot_root,unshare" -- ./your-python.py
```

[man 1 tar](https://linux.die.net/man/1/tar) - When unpacking using GNU tar then -C sets the target dir for extraction.

[man 8 pivot_root](https://linux.die.net/man/8/pivot_root) - The shell command to execute libc/syscall function. Keeps the original root available under alternative directory.

[man 8 switch_root](https://linux.die.net/man/8/switch_root) - Moves /proc, /sys and /dev (the essential pseudo-filesystem) into new root and starts init. This command does not make the old root available.

[man 7 capabilities](https://linux.die.net/man/7/capabilities) - Some capabilities you might need when mangling with networking for example CAP_NET_ADMIN.

*__Note:__ When running on __Centos/Redhat__ then you have to explicitly enable the user namespace by adding this ```user_namespace.enable=1``` as kernel argument into ```grub.cfg``` or other bootloader.*

## LibC functions man pages

There is a pretty good reference for libc functions behind the command line utility and bridge to the syscall.

* [man 2 unshare](https://linux.die.net/man/2/unshare) 
* [man 2 pivot_root](https://linux.die.net/man/2/pivot_root)

## Root filesystems

In order to make shell happy you should have a whole filesystem. All that acompanied by proper ```/proc```, ```/dev``` and ```/sys``` in place (and acordingly context aware). This can be achieved by few alternative ways.

*__Note:__ that when creating, extracting the rootfs as a regular user you might face some permission denied. You can just ignore them while extracting. For example alpine rootfs, there is a complaint about ```mknod ./dev/null c 1 3``` which requires root privileges. Despite you should ignore them when extracting as regularr user. You should handle them when becoming super user inside the inner execution context. Or you can do the extraction as root.*

### Turn docker into rootfs

If you already have a docker image you can pack the flattened layer hierarchy into tar archive which in turn (on the fly) can be extracted into target directory.

```bash
mkdir /tmp/img
docker export $(docker create centos) | tar -C /tmp/img/ -xvf -
```

### Debootstrap

This is a handy way how to prepare filesystem from any Debian or derive distribution. It actually makes similar steps as is done in standard installation process. Next steps can be done via ```chroot /target/dir```.

[Deb Wiki: Debootstrap](https://wiki.debian.org/Debootstrap)

[For Redhaters and Fedorars](https://rwmj.wordpress.com/2009/03/05/fedora-equivalent-of-debootstrap/) - To do the similar process using ```yum```.

### Alpine Rootfs

Alpine linux is a compact linux distribution and is heavily used in docker for its small size. In some sense it is not fully fleged distribution but is pretty enough for many use-cases. From known issues it is worth to mention issues: java instalation, complete locales support.

[Alpine downloads](https://alpinelinux.org/downloads/) - The main download page.

[alpine-minirootfs-3.7.0-x86_64.tar.gz](http://dl-cdn.alpinelinux.org/alpine/v3.7/releases/x86_64/alpine-minirootfs-3.7.0-x86_64.tar.gz) - The current (as of writing this text) root fs direct link.

## C example of unshare

While browsing the internet there was also similar attempt done by C lovers.

[pivot_root.c](https://github.com/hpc/charliecloud/blob/master/examples/syscalls/pivot_root.c)

