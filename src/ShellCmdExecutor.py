import subprocess
from conf import projConst

class ShellCmdExecutor(object):

    @classmethod
    def executeSync(cls, cmd, dryRun = False, isPrint = False):
        if dryRun:
            print cmd
            return cmd
        else:
            child = subprocess.Popen([cmd], cwd = projConst.git_root_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, error = child.communicate()
            if child.returncode != 0 or isPrint == True:
                print output
            return output

