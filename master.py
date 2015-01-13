import utils
from conf import projConst
from DictAddrReader import DictAddrReader
from ShellCmdExecutor import ShellCmdExecutor

from joblib import Parallel, delayed
import multiprocessing

def createBundleToSlave(env, envData):
    keyBelongsGroups = map(lambda group: group + "_*.pub", DictAddrReader.readByPath("groupList", envData).split(','))
    planToShipFiles = keyBelongsGroups + projConst.fileToShip.split(',')
    findExp = utils.findExpConstructFromList(planToShipFiles)

    slaveConfAbsPath = utils.recoverStringByDict(projConst.confTemplate['slaveConfAbsPath'], {"HOSTSET": env, })
    utils.flushDictToFile(
        {'env': env,
         'envData': envData
        }
        , slaveConfAbsPath)

    pushFileAbsPath = utils.recoverStringByDict(projConst.confTemplate['pushFileAbsPath'], {"EXPS": findExp, "HOSTSET": env, })
    pushFileName = utils.recoverStringByDict(projConst.confTemplate['pushFileName'], {"HOSTSET": env, })

    tar_to_ship_CMD = utils.recoverStringByDict(projConst.cmdTemplate['tar_to_ship'], {"EXPS": findExp, "FILE": pushFileAbsPath,})
    ShellCmdExecutor.executeSync(tar_to_ship_CMD)
    
    return (pushFileAbsPath, pushFileName,)

def process(ip, port, sshKeyPath, pushFileAbsPath, pushFileName):
    scp_file_to_host_CMD = utils.recoverStringByDict(
        projConst.cmdTemplate['scp_file_to_host'],
        {"PORT": port, "SSHKEYPATH": sshKeyPath, "IP": ip, "FILE": pushFileAbsPath,}
    )
    ShellCmdExecutor.executeSync(scp_file_to_host_CMD)

    slaveCmd_CMD = utils.recoverStringByDict(
        projConst.cmdTemplate['slaveCmd'],
        {
            "FILE": pushFileName,
        }
    )

    ssh_with_cmd_CMD = utils.recoverStringByDict(
        projConst.cmdTemplate['ssh_with_cmd'],
        {
           "PORT": port,
               "SSHKEYPATH": sshKeyPath,
               "IP": ip,
               "CMD": slaveCmd_CMD,
        }
    )   
    ShellCmdExecutor.executeSync(ssh_with_cmd_CMD)

def main():
    
    # get all hostSets
    confDict = utils.getDictFromFile(projConst.cusConfPath)
    hostSets = DictAddrReader.readByPath("hostSets", confDict)
    num_cores = multiprocessing.cpu_count()
    for env, envData in hostSets.items():
        port = DictAddrReader.readByPath("port", envData)
        sshKeyPath = DictAddrReader.readByPath("sshKeyPath", envData)
        ipList = DictAddrReader.readByPath("ipList", envData).split(',')
        pushFileAbsPath, pushFileName = createBundleToSlave(env, envData)
        Parallel(n_jobs=num_cores)(delayed(process)(ip, port, sshKeyPath, pushFileAbsPath, pushFileName) for ip in ipList)


if __name__ == '__main__':
    main()
