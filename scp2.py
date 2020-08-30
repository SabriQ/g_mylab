#!/usr/bin/env python
#wraps up rsync to synchronize two directories
from subprocess import call
import sys
import time

source = "/tmp/hbchen/" #Note the trailing slash
target = "/tmp/herb"
rsync = "rsync"
arguments = "-av"
cmd = "%s %s %s %s" % (rsync, arguments, source, target)

def sync():
    while True:
        ret = call(cmd, shell=True)
        #print cmd
        if ret !=0:
            print "resubmitting rsync"
            time.sleep(30)
        else:
            print "rsync was succesful"
            sys.exit(0)
sync()


email

#!/usr/bin/env python
#wraps up rsync to synchronize two directories
from subprocess import call
import sys
import time

"""this motivated rysnc tries to synchronize forever"""

source = "/tmp/sync_dir_A/" #Note the trailing slash
target = "/tmp/sync_dir_B"
rsync = "rsync"
arguments = "-av"
cmd = "%s %s %s %s" % (rsync, arguments, source, target)

def sync():
    while True:
        ret = call(cmd, shell=True)
        if ret !=0:
            print "resubmitting rsync"
            time.sleep(30)
        else:
            print "rsync was succesful"
            subprocess.call("mail -s 'jobs done' 88fly@163.com", shell=True)
            sys.exit(0)
sync()