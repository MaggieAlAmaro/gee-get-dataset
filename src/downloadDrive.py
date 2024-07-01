import ee
import time
from typing import Optional

from src.other.logger import MasterLogger
from src.interfaces.download import Download


class DownloadDrive(Download):
    def __init__(self) -> None:
        super().__init__(self)

    @staticmethod
    def eeExport(
        image: ee.Image,
        scale: float,
        description: str,
        fileName: str,
        region: Optional[ee.Geometry] = None,
        crs: str = 'EPSG:4326',
        fileFormat: str = 'GeoTIFF',
        folder: str = 'EuropeRGB'
    ) -> ee.batch.Task:
        """
        Exports an Earth Engine image to Google Drive.

        Args:
            image (ee.Image): The image to export.
            scale (float): The resolution in meters per pixel.
            description (str): A description of the task.
            fileName (str): The output name of the file to export.
            region (Optional[ee.Geometry], optional): The region to export. Defaults to None -> Uses complete image region.
            crs (str, optional): The coordinate reference system. Defaults to 'EPSG:4326'.
            fileFormat (str, optional): The file format. Defaults to 'GeoTIFF'.
            folder (str, optional): The folder to export to. Defaults to 'EuropeRGB'.

        Returns:
            ee.batch.Task: The export task.
        """
        
        if region is not None:
            task = ee.batch.Export.image.toDrive(
                image=image,
                description=description,
                scale=scale,
                fileNamePrefix=fileName,
                folder=folder,
                crs=crs,
                region=region,
                fileFormat=fileFormat
            )
        else:
            task = ee.batch.Export.image.toDrive(
                image=image,
                description=description,
                scale=scale,
                fileNamePrefix=fileName,
                folder=folder,
                crs=crs,
                fileFormat=fileFormat
            )
        task.start()
        return task


    @staticmethod
    def get(currentCoord, image,  logger : MasterLogger, **exportArgs):        
        try:
            logger.currentLogger.info(str(currentCoord))
            task = DownloadDrive.eeExport(image=image, **exportArgs)   
            # t = ee.data.getOperation(taskId)   
            # print(t['metadata']['state'])
        except Exception as e:
            logger.errorLogger.error("ERROR Exporting Coordinates: " +  str(currentCoord))
            print("Exception while exporting. Coordinates logged. Continuing... ")
            print("\n",e,"\n")
            return False
        
        if task is not None:
            while(str(task.status()['state']) != 'FAILED' and str(task.status()['state']) != 'COMPLETED' 
                    and str(task.status()['state']) != 'CANCELLED'):
                print(task.status()['state'])
                time.sleep(5)
            status = task.status()['state']

            if status == 'FAILED' or status == 'CANCELLED':         
                logger.errorLogger.error(f"ERROR Exporting to Google Drive. Status: {status}. Coordinates: " +  str(currentCoord))
                print(f"ERROR: Export not completed. Status: {status}. Coordinates logged. Continuing... ")
                print()
                return False
        

        logger.completedLogger.info(str(currentCoord))  
        return True

