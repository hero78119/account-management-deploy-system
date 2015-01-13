import os
import sys
from CMException import CMException

class DictAddrReader(object):

    @classmethod
    def writeByPath(cls, fullPath, obj, oriDict):
        pathFrag = fullPath.split('.')
        lastPath = ''
        curDict = oriDict
        
        for path in pathFrag:
            if lastPath and not curDict.get(lastPath, None):
                curDict[lastPath] = {}
                curDict = curDict[lastPath]
            lastPath = path
        curDict[lastPath] = obj
        
    @classmethod
    def readByPath(cls, fullPath, oriDict):  
        pathFrag = fullPath.split('.')
        curDict = oriDict
        curPath = ''
        for path in pathFrag:
            try:
                if curPath:
                    curPath += '.' + path
                else:
                    curPath += path
                curDict = curDict[path]
            except:
                raise CMException(curPath)
        return curDict    
