from typing import List, Optional, Tuple
# import time
import numpy as np
import ee
from PIL import Image

from src.other.coordinates import getRegionCoordinates
from src.other.logger import MasterLogger
from src.interfaces.download import Download



class DownloadArray(Download):
    def __init__(self):
        pass


    #!!!! pixelCap may need to be adjusted in case image is returning black Lines
    @staticmethod
    def get256ImageArray(
        coords: List[List[float]],
        bandName: str,
        datasetImage: ee.Image,
        nullPixelValue: Optional[float] = None,
        pixelCap: int = 256
    ) -> np.ndarray:
        """
        Get a 256x256 image array from Earth Engine and return it as a numpy array.

        Args:
            coords (List[List[float]]): The coordinates of the polygon to get data from.
            bandName (str): The name of the band to get data from.
            datasetImage (ee.Image): The Earth Engine image to get data from.
            nullPixelValue (Optional[float]): The value to use for null pixels.
            pixelCap (int): The size of the image to get data for.

        Returns:
            np.ndarray: The image data as a numpy array.
        """
        roi = ee.Geometry.Polygon(coords)
        if nullPixelValue is not None:
            col = datasetImage.sampleRectangle(
                region=roi, properties=[bandName], defaultValue=nullPixelValue
            )
        else:  # !!!! WARNING: if there are null pixels this will throw an error
            col = datasetImage.sampleRectangle(region=roi, properties=[bandName])
        arr = col.get(bandName)
        arr = np.array(arr.getInfo())
        return arr[:pixelCap, :pixelCap]


    @staticmethod
    def getRectangleImage(
        startCoords: List[float],
        datasetImage: ee.Image,
        bandName: str,
        logger: MasterLogger,
        nullPixelValue: Optional[float] = None,
        size: Tuple[int, int] = (1024, 1024),
    ) -> np.ndarray:
        """
        Get an image from Earth Engine and return it as a numpy array.

        Args:
            startCoords (List[float]): The coordinates of the top-left corner of the image.
            datasetImage (ee.Image): The Earth Engine image to get data from.
            bandName (str): The name of the band to get data from.
            logger (MasterLogger): The logger to use for logging errors.
            nullPixelValue (Optional[float]): The value to use for null pixels.
            size (Tuple[int, int]): The size of the image to get data for.

        Returns:
            np.ndarray: The image data as a numpy array.
        """

        # start = time.time()
        assert size[0] % 256 == 0 and size[1] % 256 == 0, "Size of image must be divisible by 256."

        rows = int(size[0] / 256)
        cols = int(size[1] / 256)
        imageCols: List[np.ndarray] = []
        startCoordsForRows: List[List[float]] = []
        nextCoords = startCoords

        # get first images of every row (column?)
        for _ in range(cols):
            try:
                regionBounds = getRegionCoordinates(256, nextCoords)
            except Exception as e:
                logger.errorLogger.error(f"ERROR Getting Coordinates: {nextCoords}")
                print("ERROR: Getting Coordinates.")
                print(e)
                print()
                return np.ndarray([])

            nextCoords = regionBounds[3]
            try:
                imageCols.append(
                    DownloadArray.get256ImageArray(
                        regionBounds, bandName, datasetImage, nullPixelValue, 256
                    )
                )
                startCoordsForRows.append(regionBounds[1])
            except Exception as e:
                logger.errorLogger.error(f"ERROR on sampleRectangle() with: {nextCoords}")
                print("ERROR: On sampleRectangle() request.")
                print(e)
                print()
                return np.ndarray([])

        for _ in range(1, rows):
            for j in range(cols):
                try:
                    regionBounds = getRegionCoordinates(256, startCoordsForRows[j])
                except Exception as e:
                    logger.errorLogger.error(f"ERROR Getting Coordinates: {nextCoords}")
                    print("ERROR: Getting Coordinates.")
                    print(e)
                    print()
                    return np.ndarray([])

                try:
                    temp = DownloadArray.get256ImageArray(
                        regionBounds, bandName, datasetImage, nullPixelValue, 256
                    )
                    imageCols[j] = np.r_["0", temp, imageCols[j]]
                    startCoordsForRows[j] = regionBounds[1]
                except Exception as e:
                    logger.errorLogger.error(f"ERROR on sampleRectangle() with: {nextCoords}")
                    print("ERROR: On sampleRectangle() request.")
                    print()
                    print(e)
                    return np.ndarray([])

        fullImage = np.concatenate([cols for cols in imageCols], axis=1)
        if fullImage.shape != size:
            print(f"Returned incorrect shape!!! Shape is {fullImage.shape}. RESIZING!!!")
            # fullImage = cv2.resize(fullImage, dsize=size, interpolation=cv2.INTER_NEAREST)
        int8Image = np.uint8(fullImage)

        return int8Image



    def get(currentCoord, image, bandName, logger : MasterLogger, imageMode='L', nullPixelValue=None):
        try:
            logger.currentLogger.info(str(currentCoord))
            data = DownloadArray.getRectangleImage(currentCoord, image, bandName, logger, nullPixelValue=nullPixelValue)        
        except Exception as e:
            print(e)
            print()
            print("Exception and coordinates logged. Continuing... ")
            return
        
        logger.completedLogger.info(str(currentCoord))  

        img = Image.fromarray(data)   
        img = img.convert(imageMode)
        return  img





####################################################################################
#
# Other Functions
#
####################################################################################

def getImageFromStartCoordenates(startCoords, bandName,datasetImage,nullPixelValue=None):
    regionBounds =  getRegionCoordinates(256,startCoords)
    return DownloadArray.get256ImageArray(regionBounds,bandName,datasetImage,nullPixelValue,256)


# With ee python -> not good
# def getImage():
    # samples = dataset.sample(region=geo)
    # print(samples.propertyNames().getInfo())
    # sampleNbr = samples.size().getInfo()
    # m_list = samples.toList(samples.size())
    # ncols = math.ceil(math.sqrt(sampleNbr))
    # nrows = math.ceil(sampleNbr/ncols)
    # ee.Number(samples.get('band_order')).getInfo()
    # a = np.zeros((ncols,nrows))
    # # or i, j in product(range(0, 172801, width), range(0, 68683, height)):
    # zippedData = product(range(ncols),range(nrows))
    # for i, j in zippedData:
    #     print(i)
    #     print(j)
    #     if i + j*ncols >= sampleNbr:
    #        break
    #     e = m_list.get(i + j*ncols).getInfo()['properties']['constant']
    #     a[i][j] = e
    # print(a)
    # plt.imshow(a)
    # plt.tight_layout()
    # plt.show()


