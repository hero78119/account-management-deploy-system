import json

def getDictFromFile(path):
    with open(path) as f:
        rawFileString = f.read()
        fileDict = json.loads(rawFileString, strict = False)
        f.close()
        return fileDict

def flushDictToFile(dict, path):
    with open(path, 'w+') as f:
        f.write(json.dumps(dict))
        f.close()

def recoverStringByDict(formatStr, data):
    for key, value in data.items():
        formatStr = formatStr.replace(key, str(data[key]))
    return formatStr

def findExpConstructFromList(listOfExp):
    res = ''
    for exp in listOfExp:
        res += '-name "%s" -o ' % (exp,)
    res = res[:-3]
    return res

