import Utils
from conf import projConst
from DictAddrReader import DictAddrReader
from ShellCmdExecutor import ShellCmdExecutor
from CMException import CMException

from joblib import Parallel, delayed
import multiprocessing

def _connectionTest(ip, port, sshKeyPath):
    ssh_test_CMD = Utils.recoverStringByDict(
        projConst.toolCmdTemplate['ssh_test'],
        {
           "PORT": port,
           "SSHKEYPATH": sshKeyPath,
           "IP": ip,
        }
    )   
    ShellCmdExecutor.executeSync(ssh_test_CMD, isPrint = True)

def executeShellCmd(data):
    ip = data['ip']
    port = data['port']
    sshKeyPath = data['sshKeyPath']
    cmd = data['cmd']
    ssh_exe_cmd_CMD = Utils.recoverStringByDict(
        projConst.toolCmdTemplate['ssh_exe_cmd'],
        {
           "PORT": port,
           "SSHKEYPATH": sshKeyPath,
           "IP": ip,
           "CMD": cmd,
        }
    )
    ShellCmdExecutor.executeSync(ssh_exe_cmd_CMD, isPrint = True)    


class Tools:

    @staticmethod
    def connectionTest(varBlob):
        #if varBlob.get('help', None):
        #    raise CMException()
        # get all hostSets
        confDict = Utils.getDictFromFile(projConst.cusConfPath)
        hostSets = DictAddrReader.readByPath("hostSets", confDict)
        num_cores = multiprocessing.cpu_count()
        for env, envData in hostSets.items():
            port = DictAddrReader.readByPath("port", envData)
            sshKeyPath = DictAddrReader.readByPath("sshKeyPath", envData)
            ipList = DictAddrReader.readByPath("ipList", envData).split(',')
            Parallel(n_jobs=num_cores)(delayed(_connectionTest)(ip, port, sshKeyPath) for ip in ipList)

    @staticmethod
    def initDebianSlave(varBlob):
        #if varBlob.get('help', None):
        #    raise CMException()
        # get all hostSets
        confDict = Utils.getDictFromFile(projConst.cusConfPath)
        hostSets = DictAddrReader.readByPath("hostSets", confDict)
        num_cores = multiprocessing.cpu_count()
        for env, envData in hostSets.items():
            port = DictAddrReader.readByPath("port", envData)
            sshKeyPath = DictAddrReader.readByPath("sshKeyPath", envData)
            ipList = DictAddrReader.readByPath("ipList", envData).split(',')
            Parallel(n_jobs=num_cores)(delayed(executeShellCmd)({'ip': ip, 'port': port, 'sshKeyPath': sshKeyPath, 'cmd': projConst.cmdTemplate['init_debian_slave']}) for ip in ipList)        

    @staticmethod
    def exeShellCmd(varBlob):
        #if varBlob.get('help', None):
        #    raise CMException(
        #        """
        #            suboptions for --task=exeShellCmd
        #            --cmd=<bash shell cmd>
        #        """
        #    )
        if not varBlob.get('cmd', None):
            raise CMException('must provide --cmd=SHELL_CMD')

        # get all hostSets
        confDict = Utils.getDictFromFile(projConst.cusConfPath)
        hostSets = DictAddrReader.readByPath("hostSets", confDict)
        hostSets = hostSets.items()
 
        targetHostSets = varBlob.get('envs', None)
        if targetHostSets:
            targetHostSets = targetHostSets.split(',')
            hostSets = filter(lambda (env, envData,): env in targetHostSets, hostSets)
       
        num_cores = multiprocessing.cpu_count()
        for env, envData in hostSets:
            port = DictAddrReader.readByPath("port", envData)
            sshKeyPath = DictAddrReader.readByPath("sshKeyPath", envData)
            ipList = DictAddrReader.readByPath("ipList", envData).split(',')
            Parallel(n_jobs=num_cores)(delayed(executeShellCmd)({'ip': ip, 'port': port, 'sshKeyPath': sshKeyPath, 'cmd': varBlob['cmd'],}) for ip in ipList)
