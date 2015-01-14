import __builtin__
import getopt
import sys
import os
dir_name =  os.path.dirname(os.path.realpath(__file__)) + '/tools/'
sys.path.append(dir_name)

toolsModule = __import__('Tools')
func = getattr(toolsModule, 'Tools')
allFun = filter(lambda fun: fun[0] != '_', dir(func))

def usage():
    print 'argument:'
    print '-h --help'
    #print '--shellDryrun'
    print '--task=', ['deploy'] + allFun
    print " default task is 'deploy'"

def initialize():
    __builtin__.shellDryrun = False

def main():
    initialize()
    #process argument by getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['help', 'shellDryrun', 'task='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    task = 'deploy'
    for opt, val in opts:
        if opt in ('-h', '--help',):
            usage()
            sys.exit(2)
        if opt in ('--task',):
            task = val
        if opt in ('--shellDryrun',):
            __builtin__.shellDryrun = True

    if task == 'deploy':
        import Master
        Master.main()
    else:
        try:
            getattr(func, task)()
        except Exception as e:
            print e
            print 'task %s not found!' % (task,)
            print 'all available tasks:', ['deploy'] + allFun

if __name__ == '__main__':
    main()
