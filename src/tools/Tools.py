import Utils
from conf import projConst
from DictAddrReader import DictAddrReader
from ShellCmdExecutor import ShellCmdExecutor

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
    ShellCmdExecutor.executeSync(ssh_test_CMD)


class Tools:

    @staticmethod
    def connectionTest():
        # get all hostSets
        confDict = Utils.getDictFromFile(projConst.cusConfPath)
        hostSets = DictAddrReader.readByPath("hostSets", confDict)
        num_cores = multiprocessing.cpu_count()
        for env, envData in hostSets.items():
            port = DictAddrReader.readByPath("port", envData)
            sshKeyPath = DictAddrReader.readByPath("sshKeyPath", envData)
            ipList = DictAddrReader.readByPath("ipList", envData).split(',')
            Parallel(n_jobs=num_cores)(delayed(_connectionTest)(ip, port, sshKeyPath) for ip in ipList)

