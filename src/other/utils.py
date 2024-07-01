import os, time

# Creates new filename from a given filename
# WARNING: suffix MUST hold file extention
def newFilename(oldname, prefix=None, suffix=".png", outdir='.'):
    f_type = os.path.splitext(oldname)[-1]
    newFileName = os.path.basename(oldname)
    noExtension = newFileName.rstrip(f_type)
    fn = noExtension
    if prefix != None:        
        fn = prefix + noExtension
    fn = fn + suffix
    fn = os.path.join(outdir,fn) 
    #fn = os.path.join(os.path.dirname(oldname),fn) 
    print("New filename: " + fn)
    return fn


def makeLogFolder(logFolderName, folderFunctionName):
    if(not os.path.exists(logFolderName)):
        os.mkdir(logFolderName)        
    output = os.path.join(logFolderName, (folderFunctionName + "-" + time.strftime("%Y-%m-%d-%H-%M-%S")))
    os.mkdir(output)
    return output

def makeOutputFolder(folderFunctionName):
    return makeLogFolder('output', folderFunctionName)