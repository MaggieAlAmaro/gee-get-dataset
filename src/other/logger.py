import logging, os, time, shutil, ast
from src.other.utils import makeLogFolder
def setup_logger(name, log_file, level=logging.INFO, format='default'):
    handler = logging.FileHandler(log_file)   
    if format == 'dict':
        formatter = logging.Formatter('\"%(number)s\": %(message)s,')
    else:
        formatter = logging.Formatter('%(message)s')
    formatter = handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


from src.other.coordinates import getRegionCoordinates

# TODO: check if making this file json will make it slower or not
#
# Keeps a record of images downloaded and is in charge of numbering images
# Logs Image coordinates in dict format (image_number) : [bottom_left_long-lat_coordinates]
# If file already exists, a new entry will have the number after the last entry 
# If it doesn't, starts logging at number 1
class CoordinateRecord():    
    def __init__(self, log_id, filename='coordinates.log', start_coords=[-9, 12], image_size=1024): 

        if os.path.exists(filename):
            # Read last entry.
            with open(filename,"rb") as f:
                try:  # catch OSError in case of a one line file 
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, os.SEEK_CUR)
                except OSError:
                    f.seek(0)

                try: 
                    last_line = f.readline().decode()
                    lastEntry = int(last_line.split(":")[0].replace("\"",''))
                    lastCoords = ast.literal_eval(last_line.split(":")[-1][1:-3])
                    self.nextCoords = getRegionCoordinates(image_size, lastCoords)[3]
                    self.entry = lastEntry + 1
                except ValueError:  #probably empty file
                    print("WARNING! Couldn't find last entry in COORDINATE log. Starting Count from 1...")
                    self.entry = 1
        else:
            self.nextCoords = start_coords
            self.entry = 1
            

        name = log_id + "_" + str( os.path.basename(filename.split('.')[0]))
        self.logger = setup_logger(name, filename, format='dict')

        # JSON file 
        # if os.path.exists(filename): 
        #     #read last entry.
        #     with open('img_coordinates.json',"r") as f:
        #         self.data = json.load(f)
            
        #     lastEntry = int(list(self.data)[-1])
        #     self.file = open('img_coordinates.json',"w")
        #     self.entry = lastEntry + 1
        # else:
        #     self.file = open('img_coordinates.json',"w")
        #     self.entry = 1
        #     self.data = {}


        # logJson.keys()

    def log(self, dictEntry):
        self.logger.info(dictEntry,extra={'number': self.entry})
        self.entry += 1

        # self.data[self.entry] = dictEntry
        # json.dump(self.data, self.file, indent=2)

#
# Holds all of the logs
#
class MasterLogger():
    def __init__(self, outputFolderName, prefix='') -> None:
        output = os.path.join('logs', outputFolderName)
        if not os.path.exists(output):
            os.mkdir(output)
        else:
            #Make backup of existing folder
            backupOut = makeLogFolder('backups', outputFolderName)
            for logfile in os.listdir(output):
                filepath = os.path.join(output,logfile)
                dstfilepath = os.path.join(backupOut,logfile)
                shutil.copy(filepath,dstfilepath)

        # current object logger
        self.currentLogger = setup_logger(outputFolderName+'_currentLogger', os.path.join(output, prefix + 'current.log'))
        self.currentLogger.info('Starting Session on ' + str(time.strftime("%Y-%m-%d--%Hh%Mm")))

        # request made logger
        self.requestLogger = setup_logger(outputFolderName+'_requestLogger', os.path.join(output, prefix + 'requests.log'))
        self.requestLogger.info('Starting Session on ' + str(time.strftime("%Y-%m-%d--%Hh%Mm")))
        
        # request completed logger
        self.completedLogger = setup_logger(outputFolderName+'_completedLogger', os.path.join(output, prefix + 'completed.log'))
        self.completedLogger.info('Starting Session on ' + str(time.strftime("%Y-%m-%d--%Hh%Mm")))

        # error logger
        self.errorLogger = setup_logger(outputFolderName+'_errorLogger', os.path.join(output, prefix + 'errors.log'), logging.ERROR)
        self.errorLogger.error('Starting Session on ' + str(time.strftime("%Y-%m-%d--%Hh%Mm")))
        
        #coordinate dictionary
        self.coordinateLogger = CoordinateRecord(outputFolderName, os.path.join(output, prefix + 'coordinates.log'))

        #rejected logger  --> not used -- For when arbitrary checks are not passed
        # self.rejectedLogger = setup_logger(outputFolderName+'_rejectedLogger', os.path.join(output, prefix + 'rejected.log'))
        # self.rejectedLogger.info('Starting Session on ' + str(time.strftime("%Y-%m-%d--%Hh%Mm")))
        


