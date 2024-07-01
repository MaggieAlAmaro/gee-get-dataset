import numpy as np
import ee
from PIL import Image
import math

from src.other.logger import MasterLogger
from src.other.utils import newFilename
from downloadArray import DownloadArray
from interfaces.getter import Getter

# sys.path.remove('c:\\ee')
# sys.path.append('c:\\users\\margarida\\onedrive - universidade de lisboa\\documents\\other projects\\gee-get-dataset')
# print(sys.path)


class CopernicusWater(Getter):
    def __init__(self, downloader, reprojectToSRTM=True):
        super().__init__(downloader)
        copernicus = ee.ImageCollection("COPERNICUS/DEM/GLO30")
        water = copernicus.select('WBM')
        self.mosaicWater = water.mosaic()
        
        if reprojectToSRTM:
            srtm = ee.Image('USGS/SRTMGL1_003')
            srtmProjection = srtm.projection()
            self.mosaicWater = self.mosaicWater.reproject(srtmProjection) 
        # print(self.mosaicWater.getInfo())

        self.numberOfWaterClasses = 4  


    def treatDataset(self, coords, outdir, logger : MasterLogger, **kwargs):        
        currentCoord = coords[0]
        def waterFullSpectrum(image):
            image = np.array(image)
            nbr = math.floor(255/(self.numberOfWaterClasses - 1)) # -1 because classes start at 0
            image = image * nbr
            return image
        
        waterImg = DownloadArray.get(currentCoord, self.mosaicWater, 'WBM',  logger)
        waterData = waterFullSpectrum(waterImg)
        img = Image.fromarray(waterData)   
        img = img.convert('L')
        fileName = str(logger.coordinateLogger.entry)
        fn = newFilename(fileName, outdir=outdir)
        img.save(fn)
        logger.coordinateLogger.log(currentCoord)




class SRTMLandforms(Getter):
    def __init__(self, downloader, reprojectToSRTM=True):
        super().__init__(downloader)
        dataset = ee.Image('CSP/ERGo/1_0/Global/SRTM_landforms')
        self.srtmLandforms = dataset.select('constant')
        if reprojectToSRTM:
            srtm = ee.Image('USGS/SRTMGL1_003')
            srtmProjection = srtm.projection()
            self.srtmLandforms = self.srtmLandforms.reproject(srtmProjection) 
        # print(self.srtmLandforms.getInfo())


    def treatDataset(self, coords, outdir, logger : MasterLogger, **kwargs):        
        currentCoord = coords[0]
        segImg = DownloadArray.get(currentCoord, self.srtmLandforms, 'constant', logger, nullPixelValue=0)
        fileName = str(logger.coordinateLogger.entry)
        fn = newFilename(fileName, outdir=outdir)
        segImg.save(fn)
        logger.coordinateLogger.log(currentCoord)
    





class SegmentationMask():
    def __init__(self, downloader, reprojectToSRTM=True):
        self.water = CopernicusWater(downloader, reprojectToSRTM)
        self.srtmLandforms = SRTMLandforms(downloader, reprojectToSRTM)
        
    def get(self, coords, outWater, outSegment, loggerWater : MasterLogger, loggerSegment : MasterLogger):
        currentCoord = coords[0]
        print("On coordinates", currentCoord)
        try:
            self.water.treatDataset(coords, outWater, loggerWater)
            try:
                self.srtmLandforms.treatDataset(coords, outSegment, loggerSegment)                
            except Exception as e:
                loggerWater.errorLogger.error("Exception: Generation Error (gettting image): " + str(currentCoord))
                print("Exception: Water Dataset Error. Continuing... ")
                print(e)

        except Exception as e:
            loggerSegment.errorLogger.error("Exception: Generation Error (exporting image): " + str(currentCoord))
            print("Exception: Segmentation Dataset Error. Continuing... ")
            print(e)
        







