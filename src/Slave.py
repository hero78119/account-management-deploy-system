import Utils
from conf import projConst
import glob
import os 
import re
from DictAddrReader import DictAddrReader
from ShellCmdExecutor import ShellCmdExecutor

regexp = {
    'match_group_user': re.compile('(.*)\_(.*)\.pub'),
}

def updateUserPubKeys(user, group):
    update_user_pub_key_CMD = Utils.recoverStringByDict(
             projConst.cmdTemplate['update_user_pub_key'],
             {"USERNAME": user, "GROUP": group,}
        )
    ShellCmdExecutor.executeSync(update_user_pub_key_CMD)

def addUserWithGroup(users, group):
    for user in users:
        add_user_with_group_CMD = Utils.recoverStringByDict(
                 projConst.cmdTemplate['add_user_with_group'],
                 {"USERNAME": user, "GROUP": group,}
            )
        ShellCmdExecutor.executeSync(add_user_with_group_CMD)        
        updateUserPubKeys(user, group)

def delUser(delUsers):
    for delUser in delUsers:
        rm_user_CMD = Utils.recoverStringByDict(
                 projConst.cmdTemplate['rm_user'],
                 {"USERNAME": delUser,}
            )
        ShellCmdExecutor.executeSync(rm_user_CMD)

def appendUsersToSudo(newSudoUsers):
    for newSudoUser in newSudoUsers:
        append_user_to_sudo_CMD = Utils.recoverStringByDict(
                 projConst.cmdTemplate['append_user_to_sudo'],
                 {"USERNAME": newSudoUser,}
            )
        ShellCmdExecutor.executeSync(append_user_to_sudo_CMD)

def delUsersFromSudo(delSudoUsers):
    for delSudoUser in delSudoUsers:
        rm_user_from_sudo_CMD = Utils.recoverStringByDict(
                 projConst.cmdTemplate['rm_user_from_sudo'],
                 {"USERNAME": delSudoUser,}
            )
        ShellCmdExecutor.executeSync(rm_user_from_sudo_CMD)    

def main():
    groupUserMap = {}
    # build group -> users mapping
    for file in os.listdir(projConst.defaultRes):
        match = regexp['match_group_user'].match(file)
        if not match:
            continue

        group = match.group(1)
        user = match.group(2)
        if not groupUserMap.get(group, None):
            groupUserMap[group] = []
        groupUserMap[group].append(user)
    
    for file in glob.glob(projConst.runtimeTmp + "slaveProj_*.json"):
        slaveConfigPath = file
    slaveConfig = Utils.getDictFromFile(slaveConfigPath)
    
    groups = DictAddrReader\
                  .readByPath('envData.groupList', slaveConfig)\
                  .split(',')
    for group in groups:

        add_group_CMD = Utils.recoverStringByDict(
                 projConst.cmdTemplate['add_group'],
                 {"GROUP": group,}
            )
        ShellCmdExecutor.executeSync(add_group_CMD)
         
 
        get_users_in_group_CMD = Utils.recoverStringByDict(
                 projConst.cmdTemplate['get_users_in_group'],
                 {"GROUP": group,}
            )
        usersInSystem = filter(lambda u: len(u) > 0, ShellCmdExecutor.executeSync(get_users_in_group_CMD).rstrip().split(' '))
        usersInSystem = set(usersInSystem)
        targetUsers = set(groupUserMap.get(group, []))
 
        delUsers = list(usersInSystem.difference(targetUsers))
        
        targetUsersList = list(targetUsers)
        addUserWithGroup(targetUsersList, group)
        delUser(delUsers)
    
    # sudo group process 
    get_users_in_sudo_group_CMD = projConst.cmdTemplate['get_users_in_sudo_group']
              
    sudoUsersInSystem = filter(lambda u: len(u) > 0, ShellCmdExecutor.executeSync(get_users_in_sudo_group_CMD).rstrip().split(' '))
    sudoUsersInSystem = set(sudoUsersInSystem)

    sudoGroups = DictAddrReader\
                  .readByPath('envData.sudoGroups', slaveConfig)\
                  .split(',')

    targetSudoUsers = set()
    for sudoGroup in sudoGroups:
        targetSudoUsers = targetSudoUsers.union(set(groupUserMap.get(sudoGroup, [])))

    newSudoUsers = list(targetSudoUsers.difference(sudoUsersInSystem))
    delSudoUsers = list(sudoUsersInSystem.difference(targetSudoUsers))
    appendUsersToSudo(newSudoUsers)
    delUsersFromSudo(delSudoUsers)
    
if __name__ == '__main__':
    main()

