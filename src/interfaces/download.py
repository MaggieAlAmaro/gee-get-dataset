from abc import ABC, abstractmethod
from typing import List, Dict, Any
import ee
from src.other.logger import MasterLogger

class Download(ABC):
    """Interface class for downloading data from GEE"""

    @abstractmethod
    def get(
        self,
        currentCoord: List[float],
        image: ee.Image,
        logger: MasterLogger,
        **kwargs: Dict[str, Any]
    ) -> None:
        """
        Interface method for downloading data from GEE

        Args:
            currentCoord (List[float]): List of coordinates in the format [longitude, latitude]
            image (ee.Image): Image to download
            logger (MasterLogger): Logger for logging any errors
            kwargs (Dict[str, Any]): Other arguments

        Returns:
            None
        """
        pass

