
import argparse, os, ee

from src.downloadDrive import DownloadDrive
from src.downloadArray import DownloadArray
from src.coordinateLoop import CoordinateLoop

from src.other.logger import MasterLogger
from src.examples.SrtmLandformsAndWater import SegmentationMask, CopernicusWater
from src.examples.SrtmAndLandsat import SRTM, Landsat


def parse_args():
    parser = argparse.ArgumentParser(description='Command line tool for iterative downloading Google Earth Engine datasets.')
    parser.add_argument('--name', type=str,  help='Name of a download session. \
                                                            If the name is new it will create a new logging and output folder with this name. \
                                                            If the name exists it will append to the existing session and download to respective output folder.')
    parser.add_argument('--download_type', type=str, choices=['Drive', 'Array'], help='Type of download.', default='Array')
    parser.add_argument('--dataset', type=str, choices=['SRTM', 'LANDSAT', 'Water', 'MASK'], help='Dataset to download.', default='Water')
    parser.add_argument('--image_size', type=int, help='Image resolution. Only supports single number for now.', default=1024)
    return parser.parse_args()

def setupFolders():
    if(not os.path.exists('logs')):
        os.mkdir('logs')     
    if(not os.path.exists('output')):
        os.mkdir('output')        
    if(not os.path.exists('backups')):
        os.mkdir('backups')        



def getGEEDataset(session_name, download_type, dataset, image_size):

    #### Define Region Of Interest Bounds
    # For whole world: The SRTM data is somewhere between 60° north and 56° south latitude so:
    # minLat = -56
    # maxLat = 60
    # minLong = -180
    # maxLong = 180

    #### For Europe and a little Africa
    minLat=12
    maxLat=60
    minLong=-9 
    maxLong=60

    #### Define Start Coordinate -> Bottom-left of ROI bound
    start_coord = [minLong, minLat]

    
    #### Define Downloader
    # TODO: This doesn't do anything yet
    # Must use self.downloader inside children of Getter - currently hard coding the type of download
    downloader = None
    if download_type == 'Drive':
        downloader = DownloadDrive
    elif download_type == 'Array':     
        downloader = DownloadArray

    
    #### Define Getter, Logger, Output Folder
    dataset_getter = None
    getter_args = None

    if dataset != 'MASK':
        logger = MasterLogger(session_name, start_coord)
        outdir = f"output\\{session_name}"
        os.makedirs(outdir, exist_ok=True)
        start_coord = logger.coordinateLogger.nextCoords

        if dataset == 'SRTM':
            dataset_getter = SRTM(downloader)
            getter_args = { 'imageSize': image_size, 'outdir' : outdir, 'logger': logger}
        elif dataset == 'LANDSAT':
            dataset_getter = Landsat(downloader)
            getter_args = { 'imageSize': image_size, 'outdir' : outdir, 'logger': logger }
        elif dataset == 'Water':
            dataset_getter = CopernicusWater(downloader)
            getter_args = {'outdir' : outdir, 'logger': logger}

    elif dataset == 'MASK':
        dataset_getter = SegmentationMask(downloader)        
        output_seg = f"output\\seg_{session_name}"
        output_water = f"output\\water_{session_name}"
        os.makedirs(output_seg, exist_ok=True)
        os.makedirs(output_water, exist_ok=True)
        water_logger = MasterLogger(f'water_{session_name}')
        segment_logger = MasterLogger(f'segment_{session_name}')
        getter_args = { 'outWater': output_water, 'outSegment': output_seg, 'loggerWater': water_logger, 'loggerSegment': segment_logger}
        start_coord = segment_logger.coordinateLogger.nextCoords


    #### Start Loop
    loop = CoordinateLoop()
    loop.coordinateLoop(dataset_getter.get, image_size, start_coord, **getter_args)



if __name__ == '__main__':
    # ee.Authenticate()
    ee.Initialize(project='ee-terrain-maggie')

    setupFolders()
    args = parse_args()    
    getGEEDataset(args.name, args.download_type, args.dataset, args.image_size)
    


###############################
# Coords
###############################
# prettyCoords = [-0.046, 38.696]
# startCoord = [-4.1644444444444435, 31.34222222222213]
# startCoord = [-6.155555555555555, 37.031111111111045]
# startCoord = [3.5155555555555575, 46.133333333333326]
# startCoord = [35.08888888888881, 37.31555555555549] 
# startCoord = [39.9244444444444, 32.19555555555546]~
# startCoord = [45.04444444444443, 24.231111111111062]
# startCoord = [55.85333333333339, 52.1066666666667]


###############################
# Geometry 
###############################
# geometry1 = ee.Geometry.Polygon([
    # [-6.055555555555555, 37.031111111111045], 
    # [-6.055555555555555, 37.11555555555549], 
    # [-5.9711111111111105, 37.11555555555549], 
    # [-5.9711111111111105, 37.031111111111045] ])
# geometry2 = ee.Geometry.Point([-6.055555555555555, 37.031111111111045])

