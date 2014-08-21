# -*- coding: UTF-8 -*-
'''
    author: yonka
    date: 2014-03-08
    comment: based on some existed example

    history: ...
'''

# Core modules
# import atexit
import os
import sys
import time
import datetime
import signal
import json
import setproctitle

now = datetime.datetime.now


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(
            self, pidfile=None, logfile=None, name=None,
            uid=None, gid=None, force=False, exitparent=True,
            stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
        self.name = name
        self.uid = uid if uid else os.getuid()
        self.gid = gid if gid else os.getgid()
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.single = False if pidfile is None else True
        self.pidno = 0
        self.force = force
        self.exitparent = exitparent

    def get_proc_info(self):
        pid = os.getpid()
        ppid = os.getppid()
        pgid = os.getpgid(pid)
        sid = os.getsid(pid)
        procname = setproctitle.getproctitle()
        # return "pid: %s; pgid: %s; sid: %s; procname: %s" % (
        #     pid, pgid, sid, procname)
        proc_info = {
            'pid': pid,
            'ppid': ppid,
            'pgid': pgid,
            'sid': sid,
            'procname': procname
        }
        return proc_info

    def change_proc_name(self):
        """
        Change the name of the process.
        """
        try:
            setproctitle.setproctitle(self.name)
        except ImportError:
            pass

    def change_user_grp(self):
        #if self.uid is None and self.gid is None:
        #    return
        #else:
        #    uid = os.getuid() if self.uid is None else self.uid
        #    gid = os.getgid() if self.gid is None else self.gid
        try:
            if self.uid < 0 or self.gid < 0:
                raise ValueError("wrong value for user id or grp id\n")
            elif os.getuid() != 0:
                raise OSError(
                    "sorry. only root user can change user/group, "
                    "please execute with root role\n")
            os.setgid(self.gid)
            # setgid should be excuted before setuid
            os.setuid(self.uid)
        except (ValueError, OSError) as e:
            sys.stderr.write(str(e))
            sys.exit(1)

    def change_stdfds(self):
        try:
            original_stderr = sys.stderr
            si = file(self.stdin, 'r')
            so = file(self.stdout, 'a+')
            se = file(self.stderr, 'a+', 0)
            sys.stdout.flush()
            sys.stderr.flush()
            print 'start to change stdfds'
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())
        except OSError:
            original_stderr.write("can not establish std fd...\n")
            sys.exit(1)

    def register_grace_exit(self):
        signal.signal(signal.SIGTERM, self.grace_exit)
        signal.signal(signal.SIGINT, self.grace_exit)

    def grace_exit(self, signo=None, stack_frame=None):
        msg = "pid %s exit... time: %s\n" % (self.pidno, now().isoformat())
        if signo is not None:
            msg = "receive signal %s, %s" % (signo, msg)
        sys.stderr.write(msg)
        if self.single:
            self.delpidfile()
        sys.exit(0)

    def daemonize(self):
        """
        Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                if self.exitparent:
                    # Exit first parent
                    sys.exit(0)
                else:
                    return False
            self.change_proc_name()
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (
                e.errno, e.strerror))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (
                e.errno, e.strerror))
            sys.exit(1)

        print json.dumps(self.get_proc_info(), indent=1, ensure_ascii=False)

        self.pidno = os.getpid()
        if self.single:
            self.createpidfile()

        sys.stderr.write("before change user&group, uid is %s, gid is %s\n" % (
            os.getuid(), os.getgid()))
        self.change_user_grp()
        sys.stderr.write("after change user&group, uid is %s, gid is %s\n" % (
            os.getuid(), os.getgid()))

        self.change_stdfds()

        self.register_grace_exit()

        return True

    def createpidfile(self):
        # Write pidfile
        # atexit.register(self.delpidfile)
        # as we use signal to do clean up things...
        # Make sure pid file is removed if we quit
        pid = str(self.pidno)
        try:
            file(self.pidfile, 'w+').write("%s\n" % pid)
            os.chown(self.pidfile, self.uid, self.gid)
            stat = os.stat(self.pidfile)
            print "chown file %s to %s %s finished\n" % (
                self.pidfile, stat.st_uid, stat.st_gid)
        except Exception as e:
            sys.stderr.write("pidfile creation failure...\n")
            sys.stderr.write(str(e))
            sys.exit(1)

    def delpidfile(self):
        try:
            os.remove(self.pidfile)
            print "remove pidfile %s" % self.pidfile
        except:
            sys.stderr.write("pidfile remove failure...")
            return False
        else:
            return True

    @property
    def pid(self):
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None
        return pid

    @property
    def current_status(self):
        """
        Status of the daemon.
        """
        if self.single:
            pid = self.pid
            running = True if pid else False
            return running
        else:
            return False

    def status(self):
        """
        Status of the daemon.
        """
        status = self.current_status
        if status:
            if self.single:
                print '%s start/running, process %s' % (self.name, self.pid)
            else:
                print '%s start/running.' % (self.name,)
        else:
            print '%s stopped/waiting.' % (self.name,)
        return status

    def guard(self):
        pid = self.pid
        if pid:
            import psutil
            proc = psutil.Process(pid)
            status = proc.status
            print '%s %s, process %s' % (self.name, status, pid)
            if status in (
                    psutil.STATUS_DEAD, psutil.STATUS_STOPPED,
                    psutil.STATUS_ZOMBIE):
                self.logger.warn(
                    '%s is in status of %s, restarting...', self.name, status)
                try:
                    self.stop()
                    self.start()
                except Exception, e:
                    self.logger.exception('Failed to restart %s.', self.name)
                    print e
            elif status in (psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING):
                self.logger.info('%s is still running.', self.name)
            else:
                self.logger.info(
                    '%s is in unknown status %s.', self.name, status)
        else:
            self.logger.info('%s stopped manually.', self.name)

    def start(self):
        """
        Start the daemon
        """
        if self.single:
            pid = self.pid

            if pid:
                if not self.force:
                    message = \
                        "pidfile %s already exists. Is it already running?\n"
                    sys.stderr.write(message % self.pidfile)
                    sys.exit(1)
                else:
                    sys.stderr.write(
                        "found pidfile, clear it as in force mode\n")
                    res = self.delpidfile()
                    if not res:
                        sys.stderr.write("clear old pidfile failed, exit...\n")
                        sys.exit(1)

        # Start the daemon
        daemonresult = self.daemonize()
        if daemonresult:
            self.run()

    def stop(self):
        """
        Stop the daemon
        """
        if self.single:
            pid = self.pid

            if not pid:
                message = "pidfile %s does not exist. Not running?\n"
                sys.stderr.write(message % self.pidfile)

                # Just to be sure. A ValueError might occur if the PID file is
                # empty but does actually exist
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)

                return  # Not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
            print '%s stopped/waiting.' % (self.name,)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """
        raise NotImplemented()
