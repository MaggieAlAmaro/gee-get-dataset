

![Example Image](assets/GEEBanner.png)

<p align="center"> Iteratively fetch images with a specific size from Google Earth Engine datasets.</p>
<p align="center"> A Google account with Google Earth Engine access is <font color="orange">necessary</font>.</p>

 
## Installation

Installing with ``Conda``:
1. Create Conda environment and activate it:
```
conda env create -f environment.yml
conda activate geeData
```
2. Perform a one-time authentication:

```
earthengine authenticate
```
3. Follow the on-screen instructions.

## Usage

### Command line tool

```
usage: main.py [-h] [--name NAME] [--download_type {Drive,Array}] [--dataset {SRTM,LANDSAT,Water,MASK}] [--image_size IMAGE_SIZE]

options:
  -h, --help            show this help message and exit
  --name NAME           Name of a download session. 
        - If the name is new it will create a new  logging and output folder with this name.
        - If the name exists it will append to the existing session and download to respective output folder.
  --download_type {Drive, Array}
                        Type of download.
  --dataset {SRTM,LANDSAT,Water,MASK}
                        Dataset to download.
  --image_size IMAGE_SIZE
                        Image resolution. Only supports single number for now.

```

For a quick example, in the command prompt type:
```
python main.py --name MySRTMImages --image_size 1024
```
- The program will start a new session. This creates a new directory in the output and log folder with the _MySRTMImages_ session name.
- The program will start exporting 1024x1024 images from the GEE Nasa SRTM dataset to Google Drive.
- The program will log the progress, errors, and other information in the logs folder.


### Custom Datasets
1. Create a class that inherits from the ``Getter`` class. 
2. Instantiate the GEE dataset in the constructor and implement the ``treatDataset`` function. 
This function is used to manipulate the dataset as needed (e.g. clip color range, choose bands, check for null pixels, etc.) and to execute the download. 
To download use ``DownloadDrive.get()`` or ``DownloadArray.get()``.
3. Add the custom class to the ``getGEEDataset`` function in ``main.py``
#### Template:
```
from src.coordinateLoop import CoordinateLoop
from src.other.logger import MasterLogger
import ee

class CustomGetter(Getter):
    ##### Implement #####
  

if __name__ == '__main__':
    ee.Authenticate()
    ee.Initialize()

    image_size = 1024
    start_coord = [-9,12]

    logger = MasterLogger(session_name, start_coords)
    outdir = f"output\\{session_name}"
    os.makedirs(outdir, exist_ok=True)

    dataset_getter = CustomGetter()
    getter_args = {}  # Insert argumeents

    loop = CoordinateLoop()
    loop.coordinateLoop(dataset_getter.get, image_size, start_coord, **getter_args)

```



## Additional Info
Images are iteratively retrieved via geographical coordinates: row-wise from the bottom-up and from left to right.
At each iteration of the main loop the current geographic coordinate is made to correspond with the bottom-left of the final image, and the other coordinates are calculated w.r.t the size in pixels of the final image.

The images will be named as numbers in the order that they were downloaded. A log is used to correlate the image number to the bottom-left geographic coordinates. Additional logs record status, errors, checks, etc. All logs are backed-up every time a new session starts.


The program is **session-based**.
Each session captures the progress made in fetching images from  GEE. Sessions allow the program to resume processing from the last logged coordinates, enabling users to interrupt and later resume the image retrieval process seamlessly.

#### How Sessions Work
- Starting a Session: When you start the program, you must specify a NAME. A new session begins if the NAME is new.
- Logging Operations: As the program runs, it logs all the operations performed on the coordinates and also the image-name to coordinates correspondance.
- Resuming a Session: You can resume a session by using the same session NAME. When resuming, the program picks up from the last logged coordinates of that session.
- Ending a Session: The session ends when the program is terminated (e.g., using Ctrl-C on Windows). The final coordinates and timestamp are recorded.

Errors don't stop the program but all errors are logged. Sometimes there are server-side errors - these usually resolve themselfs after some time. 

### Supported Downloads
Currently, the program supports:
- [x] Google Drive Export 
- Local Image download
    - [x] sampleRectangle()
    - [ ] getThumbURL 
    - [ ] getdownloadURL 

Both methods are slow: approximately 13 seconds for a 1024x1024 image. Other methods haven't been tested.

### Examples

Examples are provided for downloading:
- Heightmap Dataset (Nasa SRTM) - Drive Download
- Spectral Imaging Dataset (Landsat 8 SR) - Drive Download
- Watermass Dataset (Copernicus DEM WBM) - Array Download
- MASK (Copernicus DEM WBM + Global SRTM Landforms) - Array Download


## Known Issues
- Google Drive export returns images of incorrect size - extra black lines.
- The output image size must be a square of 2 and > 256.d


## Troubleshooting
- Authentication not working:
    - Insert Google Cloud project name (registered to use Earth Engine) inside the ``ee.initialize`` call: ``ee.initialize('my-gc-project')``. Info on GC-projects [here](https://developers.google.com/earth-engine/cloud/earthengine_cloud_project_setup#create-a-cloud-project)
    - Install ``gcloud`` locally


<!-- ## Related projects -->

<!-- - [Data Batch Processing Tool]() -->
<!-- - [Terrain Semantic Mask]() -->
