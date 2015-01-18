Account Management Deploy System (AMDS)
=======
As well known, account management on unix-server, especially on larger host groups (dozens of server), is timing-cost effort and require manual operation. This project aim to solve by automatically and periodically deploying via user-defined config to add/remove user accounts and update their ssh pub keys. 

### Methodology
Assume a deploy host, called **master**, which running a cron job at background to periodically pull the latest config from remote repository. Based on the config,  **master** packs the bundle data, finds some target hosts, call **slaves**,  and parallelly ship the bundle data and trigger execution on **slaves** host. On **slaves**, based on the bundle data, each slave will add/remove/update relative user accounts and their public keys. Theoretically, **master** can  also belongs to **slaves** set.
 
### Note
* Because of operating on account management, the script is assumed running on **slaves** with *root* user. For **master**, there is no execution identity requirement but the _root_ account is preferred because this project require the ssh **PRIVATE_KEY** located on **master** for connection to other **slaves**. The project will force **master** host communicate  with **slaves** via key-authenticated ssh to highly protect the security.
*  All operation are done by triggering linux built-in commands instead of modify sensitive file such as /etc/group, sudoers, sshd_config. This would prevent from accounts system broken due to the wrong modification of these file.
* This project add new group but do not remove group. For removing user account, this project still keep their home directory.
* The project won't touch any group/users which is not in config file, Don't worry~:)
* The password of new created user is the same as their account name.
* For security, you should manually  ban the password-based ssh login of all hosts.
 
### Prerequisite
* Currently only have test on Debian-based system, for example, Ubuntu, and Mac OSX.
* On **master** host, python package *joblib* require to be installed to utilize parallel execution. Reference installation step `` pip install joblib `` 
* On **slave** host, command line tool *members* require to be installed to utilize to get all users giving a group. Reference installation step `` apt-get install members `` 

### Resources Directory and Configuration
The resources file directory assume located at *PROJECT_ROOT/res*. The configuration file assume located at *PROJECT_ROOT/res/config.json* with the following JSON format.

#### Resources Directory
The account public keys should be put under this directory with specific format.
```
   res/
       config.json //configuration file
       GROUP1_USER1.pub // format is GROUP_USER.pub
       GROUP1_USER2.pub
       GROUP2_USER1.pub
       ...
```

#### config.json

```
{
    "hostSets": {
        "prod": {   //environment1 name
            "sshKeyPath": "PATH1/TO/YOUR/KEYDIR/prod_root_private_key", //path point to the private key with use to connect to these host groups specified in ipList
            "port": 2345,                            //ssh port of slave hosts
            "ipList": "10.8.0.2,192.168.0.103",      //slave host ip separated by comma
            "groupList": "admin,sudoers,dbmanager",  //group list separated by comma
            "sudoGroups": "sudoers,dbmanager"        //groups which will promote with sudo priviledge, separated by comma.
                 //It's feasible of groupList, sudoGroups for any combination you want. Just a constrain that groupList should cover sudoGroups. 
        },
        "staging": {   //environment2 name
            "sshKeyPath": "PATH2/TO/YOUR/KEYDIR/staging_root_private_key",
            "port": 22,
            "ipList": "172.109.12.3,172.109.12.4,172.109.12.5,172.109.12.6",
            "groupList": "developers,sudoers",
            "sudoGroups": "sudoers"
        },
        "test": {   //environment3 name
            "sshKeyPath": "PATH3/TO/YOUR/KEYDIR/test_root_private_key",
            "port": 123,
            "ipList": "127.0.0.1",
            "groupList": "developers,admin",
            "sudoGroups": "admin"
        }
        ... //more environments
    }
}
```

### Installation
1. clone this project into **master** host, said the directory name as ADMS
2. fork the [template](https://bitbucket.org/hero78119/account-management-deploy-system-conf-template) project as your own repository 
2. clone your template project into ADMS/ and rename your template repo as **res** directory
2. put the public keys inside **res** directory with defined-format, ex for one of it: **res/admin_user1.pub**
3. edit the configuration file **res/config.json** as you want. Configure to assure that master can ssh to all other slaves with root identity. Also you should configure that master will be able to pull your repository by key-authentication without password required.
4. commit and push to your own remote repository
5. on **master** host, edit a cronjob to run script periodically, ex, per hour

    ```
    0  *  *  *  * sh PATH/TO/PROJECT_ROOT/run.sh 
    ```
    
6. Afterward, you can push to update the pub key your remote template repository as you want. The cronjob in master will serve to deploy to slave based on your latest config. 
7. Enjoy it :)

After setup, the project hierarchy should look like this:
```bash
PROJECT_ROOT/
        res/                => your private repository!
           config.json      //configuration file
           GROUP1_USER1.pub // format is GROUP_USER.pub
           GROUP1_USER2.pub
           GROUP2_USER1.pub
           ...
        src/
        run.sh
        README.md
``` 

### Function Verify
You can run task from command line directly to test if functional work or not by
```bash
    > sh run.sh [options [suboptions]]
    # or
    > python src/Main.py [options [suboptions]]
    # where option can be
    # -h --help
    # --task= ['deploy', 'connectionTest', 'exeShellCmd', 'initDebianSlave']
    #  default task is 'deploy'
    # 
    #  suboptions for --task=exeShellCmd
    #   --cmd=<bash shell cmd>
    #   --envs=env1,env2,...  //(optionals, default is all enrironments)

```
For example, you can use ``python src/Main.py --task=connectionTest`` to test the master/slave ssh setting works or not. If failed then some error msg will show on screen like
```
ssh: connect to host XXX.XXX.XXX.XXX port XX: Connection refused
```

