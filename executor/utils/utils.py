'''
Copyright (2019, ) Institute of Software, Chinese Academy of Sciences

@author: wuyuewen@otcaix.iscas.ac.cn
@author: wuheng@otcaix.iscas.ac.cn
'''

'''
Import python libs
'''
import os, sys, time, signal, atexit, subprocess
import random
import logger

logger = logger.set_logger(os.path.basename(__file__), '/var/log/virtlet.log')

'''
Run back-end command in subprocess.
'''
def runCmd(cmd):
    std_err = None
    if not cmd:
        return
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        std_out = p.stdout.readlines()
        std_err = p.stderr.readlines()
        if std_out:
            logger.debug(std_out)
            return str.strip(std_out[0])
        else:
            return std_out
    finally:
        p.stdout.close()
        p.stderr.close()
        
def addPowerStatusMessage(jsondict, reason, message):
    if jsondict:
        status = {'conditions':{'state':{'waiting':{'message':message, 'reason':reason}}}}
        spec = jsondict['spec']
        if spec:
            spec['status'] = status
    return jsondict

def addExceptionMessage(jsondict, reason, message):
    if jsondict:
        status = {'conditions':{'state':{'waiting':{'message':message, 'reason':reason}}}}
        spec = jsondict['spec']
        if spec:
            spec['status'] = status
    return jsondict

def updateDomainBackup(vm_json):
    domain = vm_json.get('domain')
    if domain:
        os = domain.get('os')
        if os:
            boot = os.get('boot')
            if boot:
                os['boot'] = _addListToSpecificField(boot)
        domain['os'] = os
        sec_label = domain.get('seclabel')
        if sec_label:
            domain['seclabel'] = _addListToSpecificField(sec_label)
        devices = domain.get('devices')
        if devices:
            channel = devices.get('channel')
            if channel:
                devices['channel'] = _addListToSpecificField(channel)
            graphics = devices.get('graphics')
            if graphics:
                devices['graphics'] = _addListToSpecificField(graphics)   
            video = devices.get('video')
            if video:
                devices['video'] = _addListToSpecificField(video) 
            _interface = devices.get('_interface')
            if _interface:
                devices['_interface'] = _addListToSpecificField(_interface)  
            console = devices.get('console')
            if console:
                devices['console'] = _addListToSpecificField(console)  
            controller = devices.get('controller')
            if controller:
                devices['controller'] = _addListToSpecificField(controller)  
            rng = devices.get('rng')
            if rng:
                devices['rng'] = _addListToSpecificField(rng)  
            serial = devices.get('serial')
            if serial:
                devices['serial'] = _addListToSpecificField(serial)  
            disk = devices.get('disk')
            if disk:
                devices['disk'] = _addListToSpecificField(disk)
        domain['devices'] = devices
    return vm_json

def updateDomain(jsondict):
    with open('%s/../arraylist.cfg' % os.path.dirname(__file__)) as fr:
        for line in fr:
            l = str.strip(line)
            alist = l.split('-')
            _userDefinedOperationInList('domain', jsondict, alist)
    return jsondict

def updateDomainSnapshot(jsondict):
    with open('%s/../arraylist.cfg' % os.path.dirname(__file__)) as fr:
        for line in fr:
            l = str.strip(line)
            alist = l.split('-')
            _userDefinedOperationInList('domainsnapshot', jsondict, alist)
    return jsondict

def _addListToSpecificField(data):
    if isinstance(data, list):
        return data
    else:
        return [data]

'''
Cautions! Do not modify this function because it uses reflections!
'''    
def _userDefinedOperationInList(field, jsondict, alist):
    jsondict = jsondict[field]
    tmp = jsondict
    do_it = False
    for index, value in enumerate(alist):
        if index == 0:
            if value != field:
                break;
            continue
        tmp = tmp.get(value)
        if not tmp:
            do_it = False
            break;
        do_it = True
    if do_it:
        tmp2 = None
        for index, value in enumerate(alist):
            if index == 0:
                tmp2 = 'jsondict'
            else:
                tmp2 = '{}[\'{}\']'.format(tmp2, value)
        exec('{} = {}').format(tmp2, _addListToSpecificField(tmp))
    return
    
class ExecuteException(Exception):
    def __init__(self, reason, message):
        self.reason = reason
        self.message = message       

class KubevmmException(Exception):
    def __init__(self, reason, message):
        self.reason = reason
        self.message = message      

def randomUUID():
    u = [random.randint(0, 255) for ignore in range(0, 16)]
    u[6] = (u[6] & 0x0F) | (4 << 4)
    u[8] = (u[8] & 0x3F) | (2 << 6)
    return "-".join(["%02x" * 4, "%02x" * 2, "%02x" * 2, "%02x" * 2,
                     "%02x" * 6]) % tuple(u)

def randomMAC():
    mac = [ 0x52, 0x54, 0x00,
        random.randint(0x00, 0x7f),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

class CDaemon:
    '''
    a generic daemon class.
    usage: subclass the CDaemon class and override the run() method
    stderr:
    verbose:
    save_path:
    '''
    def __init__(self, save_path, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull, home_dir='.', umask=022, verbose=1):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = save_path
        self.home_dir = home_dir
        self.verbose = verbose
        self.umask = umask
        self.daemon_alive = True
 
    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)
 
        os.chdir(self.home_dir)
        os.setsid()
        os.umask(self.umask)
 
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)
 
        sys.stdout.flush()
        sys.stderr.flush()
 
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        if self.stderr:
            se = file(self.stderr, 'a+', 0)
        else:
            se = so
 
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
 
        def sig_handler(signum, frame):
            self.daemon_alive = False
        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)
 
        if self.verbose >= 1:
            print 'daemon process started ...'
 
        atexit.register(self.del_pid)
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write('%s\n' % pid)
 
    def get_pid(self):
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None
        return pid
 
    def del_pid(self):
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)
 
    def start(self, *args, **kwargs):
        if self.verbose >= 1:
            print 'ready to starting ......'
        #check for a pid file to see if the daemon already runs
        pid = self.get_pid()
        if pid:
            msg = 'pid file %s already exists, is it already running?\n'
            sys.stderr.write(msg % self.pidfile)
            sys.exit(1)
        #start the daemon
        self.daemonize()
        self.run(*args, **kwargs)
 
    def stop(self):
        if self.verbose >= 1:
            print 'stopping ...'
        pid = self.get_pid()
        if not pid:
            msg = 'pid file [%s] does not exist. Not running?\n' % self.pidfile
            sys.stderr.write(msg)
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
            return
        #try to kill the daemon process
        try:
            i = 0
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                i = i + 1
                if i % 10 == 0:
                    os.kill(pid, signal.SIGHUP)
        except OSError, err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
            if self.verbose >= 1:
                print 'Stopped!'
 
    def restart(self, *args, **kwargs):
        self.stop()
        self.start(*args, **kwargs)
 
    def is_running(self):
        pid = self.get_pid()
        #print(pid)
        return pid and os.path.exists('/proc/%d' % pid)
 
    def run(self, *args, **kwargs):
        'NOTE: override the method in subclass'
        print 'base class run()'