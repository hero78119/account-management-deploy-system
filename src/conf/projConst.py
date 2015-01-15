import subprocess
import os

defaultUser = 'root'
defaultSudoGroup = 'sudo'
try: #master
    git_root_path = subprocess\
                 .Popen(["git", 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)\
                 .communicate()[0].rstrip() + '/'
except Exception as e:
    #slave
    git_root_path = '/%s/run/' % (defaultUser,)

runtimeTmp = git_root_path + 'tmp/'
defaultRes = 'res'
defaultResAbsPathInSlave = git_root_path + 'src/' + defaultRes
cusConfPath = defaultRes + "/config.json"

if not os.path.exists(runtimeTmp):
    os.makedirs(runtimeTmp)

fileToShip = '*.py,slaveProj_*.json,*.pub,*.json'

confTemplate = {
    "pushFileName" : "HOSTSET.tar.gz",
    "pushFileAbsPath" : runtimeTmp + "HOSTSET.tar.gz",
    "slaveConfAbsPath" : runtimeTmp + "slaveProj_HOSTSET.json",
}

cmdTemplate = {
    "tar_to_ship": 'find . -type f \\( EXPS \\) -exec tar zcvf ' + 'FILE {} +',
    "scp_file_to_host" : 'scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no  -P PORT -i SSHKEYPATH FILE %s@IP:~/' % (defaultUser,),
    "slaveCmd": "rm -rf run; mkdir run; mv FILE run/; cd run/; tar -xf FILE ./ ;" +
                "mv %s src/; cd src/; python Slave.py;" % (defaultRes,) + "cd; rm -rf run;",
    "ssh_with_cmd" : 'ssh %s@IP -p PORT -i SSHKEYPATH -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "CMD"' % (defaultUser,),
    #"set_user_password": "echo USERNAME:PASSWORD | chpasswd;",
    "add_user_with_group": "if ! id -u USERNAME >/dev/null 2>&1; then yes | adduser USERNAME --ingroup GROUP --disabled-password; echo USERNAME:USERNAME | chpasswd; fi",
    "rm_user": "userdel -r -f USERNAME",
    "append_user_to_sudo": "usermod -aG sudo USERNAME",
    "rm_user_from_sudo": "deluser USERNAME sudo",
    "add_group" : "getent group GROUP || addgroup GROUP",
    "get_users_in_group": "members GROUP",
    "get_users_in_sudo_group": "members %s" % (defaultSudoGroup, ),
    "update_user_pub_key": 'if [ ! -d "/home/USERNAME/.ssh" ]; then mkdir /home/USERNAME/.ssh; fi; cp %s/src/res/GROUP_USERNAME.pub /home/USERNAME/.ssh/authorized_keys; chown -R USERNAME:GROUP /home/USERNAME; chmod 700 /home/USERNAME/.ssh; chmod 600 /home/USERNAME/.ssh/*' % (git_root_path,),
    "init_debian_slave": 'apt-get install members',
}


toolCmdTemplate = {
    'ssh_test': 'ssh %s@IP -p PORT -i SSHKEYPATH -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "hostname; echo \'connection success!\'" ' % (defaultUser,),
    'ssh_exe_cmd': 'ssh %s@IP -p PORT -i SSHKEYPATH -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "CMD" ' % (defaultUser,),
}
