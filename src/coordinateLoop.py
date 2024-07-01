from src.other.coordinates import getRegionCoordinates
import logging, time, sys, json
from src.other.logger import setup_logger

errorExternal = setup_logger('errorLoggerExternal', 'logs\\errorExternal.log', logging.ERROR)
errorExternal.error('New Start: ' + str(time.strftime("%Y-%m-%d-%H-%M")))

class CoordinateLoop():
    def __init__(self, minLat=12, maxLat=60, minLong=-9, maxLong=60) -> None:
        self.minLat = minLat
        self.maxLat = maxLat
        self.minLong = minLong
        self.maxLong = maxLong

    #going from bottom-left to top-right by row
    def coordinateLoop(self, downloadFunction, imgSize, startCoord, **kwargs):
        currentCoord = startCoord 
        try:
            while True:
                try:
                    coords = getRegionCoordinates(imgSize, currentCoord)      
                except Exception as e:
                    errorExternal.error("Exception: Connection Error (getting coords): " + str(currentCoord))
                    print("SERVER FAIL - Getting Coordinates. Logging start coordenates. Continuing...")
                    print(e)
                    continue

                if(coords[1][1] > self.maxLat):
                    print("REACHED OUT OF BOUNDS LATITUDE. STOPPING.")
                    break
                elif(coords[2][0] > self.maxLong):
                    currentCoord = [self.minLong,coords[2][1]] #reset long, next lat, i.e going to next column in same row
                else:
                    currentCoord = coords[3] #next long, same lat, i.e going to next column in same row
                

                # TODO: MAYBE WRAP THIS IN TRY CATCH                
                downloadFunction(coords, **kwargs)

                
                print()
                print("-----------------------------------------------")
                print()

        except KeyboardInterrupt:
            errorExternal.error("Exception: Keyboard Interrupt:" + str(coords[0]))
            print("CLIENT FAIL: Keyboard Interrupt. Logging coordenates ... Stopping.")
            sys.exit()



    def loopFromCoordinateJson(jsonFilename, downloadFunction, imgSize, **kwargs):
        with open(jsonFilename, 'r') as f:
            coordinates = json.load(f)

        try:
            for currentCoord in coordinates:
                try:
                    coords = getRegionCoordinates(imgSize, currentCoord)      
                except Exception as e:
                    errorExternal.error("Exception: Connection Error (getting coords): " + str(currentCoord))
                    print("SERVER FAIL - Getting Coordinates. Logging start coordenates. Continuing...")
                    print(e)
                    continue

                downloadFunction(coords, **kwargs)

                print()
                print("-----------------------------------------------")
                print()

        except KeyboardInterrupt:
            errorExternal.error("Exception: Keyboard Interrupt:" + str(coords[0]))
            print("CLIENT FAIL: Keyboard Interrupt. Logging coordenates ... Stopping.")
            sys.exit()

