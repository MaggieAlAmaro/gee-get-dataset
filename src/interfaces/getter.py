from src.other.logger import MasterLogger
from interfaces.download import Download

class Getter():
    """
    A class for getting images from Google Earth Engine datasets.
    Override the treatDataset class with the desired dataset treatment.

    Args:
        downloader (Download): An instance of the Download class.
    """
    def __init__(self, downloader : Download):
        self.downloader = downloader

    def treatDataset(self, **kwargs):
        pass

    def get(self, coords, outdir, logger : MasterLogger, **kwargs): 
        print("On coordinates", coords[0])
        try:
            self.treatDataset(coords, outdir, logger, **kwargs)
        except Exception as e:
            logger.errorLogger.error("Exception: Getter Error (exporting image): " + str(coords[0]))
            print("Exception: Getter Error. Continuing... ")
            print(e)

