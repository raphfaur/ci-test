from qmp import QEMUMonitorProtocol
import threading, subprocess
import time
import argparse
import re
import sys


parser = argparse.ArgumentParser()
parser.add_argument("--kint")
parser.add_argument("--time_before_tests")
args = parser.parse_args()

logs_path = "logs"

print("Starting VM")
vm = subprocess.Popen(["qemu-system-x86_64", "-no-reboot", "-smp", "2", "-qmp", "unix:qmp.sock,server,nowait", "-d", "int,in_asm", "-D", logs_path, "/boot.img"])

print("VM started")
test = {"kint" : 0}

QMP = QEMUMonitorProtocol('qmp.sock')


search_log_Q = set()
found_log_Q = set()

class Test(threading.Thread):
    """
    An abstraction to describe a test performed in QEMU
    """
    def __init__(self, uid : int, qmp_trigger_command : str, qmp_trigger_args : dict , time : float, timeout : float, log_match : str, qmp_check_cmd : str = "", qmp_check_args : str = "", qmp_check_match : str = "") -> None:
        self.qmp_trigger_command = qmp_trigger_command
        self.time = time
        self.qmp_trigger_args = qmp_trigger_args
        self.qmp_check_cmd = qmp_check_cmd
        self.qmp_check_args = qmp_check_args
        self.log_match = log_match
        self.timeout = timeout
        self.qmp_check_match = qmp_check_match
        self.successful = False
        self.uid = uid
        threading.Thread.__init__(self)
    
    def run(self):
        begin = time.time()
        running = False
        while not running :
            if time.time() - begin < self.time :
                pass
            else :
                print(f"Triggering test {self.uid}")
                self.run_test()
                time.sleep(0.1)
                self.trigger()
                begin = time.time()
                running = True
        
        while time.time() - begin < self.timeout and self.successful == False:
            time.sleep(self.timeout/10)
            self.test()
        if (self.uid, self.log_match) in search_log_Q :
            search_log_Q.remove((self.uid, self.log_match))


    def test(self):
        if self.log_match != "" :
            if self.uid in found_log_Q :
                self.successful = True
        elif self.qmp_check_match != "" :
            res = QMP.command(self.qmp_check_cmd, self.qmp_check_args)
            try :
                if re.findall(self.qmp_check_match, str(res)) :
                    self.successful = True
            except :
                pass

    def trigger(self):
        QMP.cmd(self.qmp_trigger_command, self.qmp_trigger_args)
    
    def run_test(self) -> bool:
        if self.log_match != "" :
            search_log_Q.add((self.uid, self.log_match))

           
TESTS : list[Test]= []

test = Test(1,"send-key", {"keys" : [{ "type": "qcode", "data": "a" }]},1,1,"INT=")
test2 = Test(2,"send-key", {"keys" : [{ "type": "qcode", "data": "a" }]},3,10,"INT=")
TESTS.append(test)
TESTS.append(test2)
            
stop_log = False

def watch_logs(p):
    global tests
    while not (len(search_log_Q) == 0 and stop_log == True) :
        line = p.stdout.readline().decode()
        succeded = []
        for test in search_log_Q :
            regex = test[1]
            if len(re.findall(regex, line)) > 0 :
                succeded.append(test)
                print(f"Test {test[0]} succedded")
                found_log_Q.add(test[0])
        for test in succeded :
            search_log_Q.remove(test)
        if not line:
            break
    
    return



def leave(q : QEMUMonitorProtocol):
    q.command('quit')


def main():
    p = subprocess.Popen(["tail", "-f", logs_path], stdout=subprocess.PIPE)
    logs =  threading.Thread(target=watch_logs, args=(p,))
    print(f"Starting log monitoring")
    logs.start()
    QMP.connect()

    time.sleep(int(args.time_before_tests))

    for test in TESTS :
        print(f"Starting test {test.uid}")
        test.start()

    for test in TESTS : 
        print(f"Joining test {test.uid}")
        test.join()
    

    stop_log = True
    p.kill()
    logs.join()

    successful = True
    for test in TESTS :
        if test.successful == False :
            successful = False
    
    if successful == True :
        print("Successful")
        leave(QMP)
        sys.exit(0)
    else : 
        print("Failed")
        leave(QMP)
        sys.exit(1)
    
if __name__ == '__main__':
    time.sleep(0.02)
    print("Starting")
    main()


