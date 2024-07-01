
# Location is bottom-left point of image, [long, lat]
# imageSize is pixel size of result image
def getRegionCoordinates(imageSize, location):
    #getcontext().prec = 6 #afraid to remove this   
    # 4503 5996 2737 0495 max fractional number in normal float percision 64bit

    # 1/3600 == 1 arc-sec == 30m (30.87)  == 1px (SRTM) 
    # appears that 0.04 = 16px
    # according to EE SRTM native scale is 30.922080775909325m
    arcsecond  = 1/3600     
    pixeloffset = arcsecond * imageSize

    coords = [location, \
                    [location[0], location[1]+ pixeloffset] , \
                    [location[0] + pixeloffset, location[1] + pixeloffset], \
                    [location[0]+ pixeloffset, location[1]]]
 
    # for c in coords: 
    #     print(c)
    
    return coords

def getRegionCoordinatesWithScale(imageSize, location,scaleMeters):
    #getcontext().prec = 6 #afraid to remove this   
    # 4503 5996 2737 0495 max fractional number in normal float percision 64bit

    # 1/3600 == 1 arc-sec == 30m (30.87)  == 1px (SRTM) 
    # appears that 0.04 = 16px
    # according to EE SRTM native scale is 30.922080775909325m
    arcsecond  = 1/3600 
    scaledArcsec = arcsecond * scaleMeters / 30.922080775909325
    pixeloffset = scaledArcsec * imageSize 
    

    coords = [location, \
                    [location[0],location[1]+ pixeloffset] , \
                    [location[0] + pixeloffset, location[1] + pixeloffset], \
                    [location[0]+ pixeloffset, location[1]]]
 
    # for c in coords: 
    #     print(c)
    
    return coords
