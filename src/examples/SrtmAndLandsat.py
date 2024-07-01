
import ee

from src.other.logger import MasterLogger
from interfaces.getter import Getter
from downloadDrive import DownloadDrive
from interfaces.download import Download


''' Retrieves an elevation SRTM image from the given coordinates and exports it to Google Drive. '''
class SRTM(Getter):
    def __init__(self, downloader : Download):
        super().__init__(downloader)
        self.srtm = ee.Image('USGS/SRTMGL1_003')

    def elevationCheck(eeImage, region, imgSize, stdCheck=False):
        elevationAreaCoverage = 1 # 0.8f -> at least 80% pixels not null 
        minStdVar = 100 

        # null pixel checks
        pixelCountDict = eeImage.reduceRegion(reducer=ee.Reducer.count(), geometry=region)
        pixelCount = pixelCountDict.getInfo()['elevation']      #this is how to access the result
        if (pixelCount/(imgSize*imgSize) < elevationAreaCoverage):
            print("Elevation Check (null-pixels): FAILED")
            return False
        
        # standard dev check
        if(stdCheck):
            stdDevDict = eeImage.reduceRegion(reducer=ee.Reducer.stdDev(), geometry=region)
            stdDev = stdDevDict.getInfo()['elevation']    
            #print(stdDev)  
            if (stdDev < minStdVar):
                print("Elevation Check (stdDev): FAILED")
                return False
        
        print("Elevation Check: PASSED")
        return True
    

    def treatDataset(self, coords, outdir, logger : MasterLogger, imageSize):#**kwargs):
        region = ee.Geometry.Polygon(coords)
        elevation_roi = self.srtm.clip(region)
        # SRTM range is from -10 to 6500 (officially, but not in reality)
        # Doesnt fit in 8 bit image, fits in signed 16bit with range -32,768 to +32,767
        elevation_16bit = elevation_roi.toInt16() 
        if (SRTM.elevationCheck(elevation_16bit, region, imageSize)):#kwargs.get('imageSize'))):
            fileName = str(logger.coordinateLogger.entry)

            exportArguments = {
                'fileName': fileName,
                'description': fileName,
                'scale': 30.922080775909325,
                'region': region
            }
            
            # self.downloader.get(coords[0], elevation_16bit, logger, **exportArguments)
            DownloadDrive.get(coords[0], elevation_16bit, logger, **exportArguments)
            logger.coordinateLogger.log(coords[0])
            return 
        else:
            # logger.rejected.info(str(logger.coordinateLogger.entry))
            print("Didn't pass elevation check. Continuing... ")
            return 






''' Retrieves a Landsat image from the given coordinates and exports it to Google Drive. '''
class Landsat(Getter):
    def __init__(self, downloader : Download):
        super().__init__(downloader)
        self.landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        self.cloudCoverLimit = 5

    def satCheck(eeImage, region, imgSize):
        satAreaCoverage = 1.0 #all pixels not null
        # null pixel checks
        pixelCountDict = eeImage.reduceRegion(reducer=ee.Reducer.count(), geometry=region, crs='EPSG:4326', scale=30.922080775909325, maxPixels=10000000)
        for _ , value in pixelCountDict.getInfo().items():
            print("looping")
            # pixelCount = pixelCountDict.getInfo()[key]  
            if (value/(imgSize*imgSize) < satAreaCoverage): 
                print("Satellite Check: FAILED")
                return False

        print("Satellite Check: PASSED")
        return True


    def treatDataset(self, coords, outdir, logger : MasterLogger, **kwargs):
        region = ee.Geometry.Polygon(coords)
        img = self.landsat.filter(ee.Filter.lessThan('CLOUD_COVER',self.cloudCoverLimit))

        img_median = img.median() 


        #Applies scaling factors.
        opticalBands = img_median.select('SR_B.').multiply(0.0000275).add(-0.2)
        thermalBands = img_median.select('ST_B.*').multiply(0.00341802).add(149.0)
        scaledImg_rgb = img_median.addBands(opticalBands, None, True).addBands(thermalBands, None, True)



        # pixelSpace_img = img_rgb.visualize(bands=['SR_B4', 'SR_B3', 'SR_B2'], min= 7219, max= 14355) 
        # img_rgb = img_median.select(['SR_B4', 'SR_B3', 'SR_B2'])
        pixelSpace_img = scaledImg_rgb.visualize(bands=['SR_B4', 'SR_B3', 'SR_B2'], min= 0.0, max= 0.3)
        
        if (Landsat.satCheck(pixelSpace_img, region, kwargs.get('imageSize'))):
            # pixelSpace_img = img_rgb.toUint8()    
            # print(pixelSpace_img.getInfo())
            fileName = str(logger.coordinateLogger.entry)
            downloadArgs = {
                'fileName': fileName,
                'description': fileName,
                'scale': 30.922080775909325,
                # 'size' : 1024,
                'region': region,
                'nullPixelValue' : 0,
            }
            # self.downloader.get(coords[0], pixelSpace_img, logger, **downloadArgs)
            DownloadDrive.get(coords[0], pixelSpace_img, logger, **downloadArgs)
            logger.coordinateLogger.log(coords[0])
            return 
        else: 
            # logger.rejected.info(str(logger.coordinateLogger.entry))
            print("Didn't pass spectral color check. Continuing... ")
            return 
        





''' Retrieves Landsat image if the SRTM image at the given coordinates is valid and exports it to Google Drive. '''
class LandsatConditionedOnSRTM(Getter):
    def __init__(self, downloader : Download):
        super().__init__(downloader)
        self.srtm = ee.Image('USGS/SRTMGL1_003')
        self.landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")

    def treatDataset(self, coords, outdir, logger : MasterLogger, **kwargs):
        region = ee.Geometry.Polygon(coords)

        elevation_roi = self.srtm.clip(region)
        elevation_16bit = elevation_roi.toInt16() 

        cloudCoverLimit = 5
        img = self.landsat.filter(ee.Filter.lessThan('CLOUD_COVER',cloudCoverLimit))

        img_median = img.median() 
        img_rgb = img_median.select(['SR_B4', 'SR_B3', 'SR_B2'])
        pixelSpace_img = img_rgb.visualize(bands=['SR_B4', 'SR_B3', 'SR_B2'], min= 7219, max= 14355) #Best visual results #, gamma=1.2
        
        if (SRTM.elevationCheck(elevation_16bit, region, kwargs.get('imageSize')) and 
            Landsat.satCheck(pixelSpace_img, region, kwargs.get('imageSize'))):
            fileName = str(logger.coordinateLogger.entry)
            exportArguments = {
                'fileName': fileName,
                'description': fileName,
                'scale': 30.922080775909325,
                'region': region
            }

            DownloadDrive.get(coords[0], pixelSpace_img, logger, **exportArguments)
            logger.coordinateLogger.log(coords[0])
            return
        else: 
            print("Didn't pass spectral color check. Continuing... ")
            return






