import ee
import geemap
import os
from datetime import datetime
from pathlib import Path

#Change the following two lines from your GEE account:
ee.Authenticate() #Will ask for your google earth engine credentials. Comment this line after running this once.
ee.Initialize(project="ee-joshisur231") #instead of "ee.joshisur231" use your project name (top right corner of the GEE code editor)

def download_image(
        image_asset_address, 
        clip=True, 
        roi=ee.FeatureCollection("projects/ee-joshisur231/assets/pa_effectiveness/nepal_boundary").geometry(), 
        output_path=None,
        **kwargs
        ):
    """
    Downloads an image from Earth Engine given a link and a region of interest (ROI).

    Parameters:
    - image_asset_address (str): A link to the image in Earth Engine.
    - roi (ee.FeatureCollection): A region of interest (ROI) specified as an Earth Engine FeatureCollection. Defaults to Nepal Boundary.
    - output_path (str): The file path to save the downloaded GeoTIFF image.
    - clip (bool, optional): Whether to clip the image to the specified ROI. Default is True.
    - Optional parameters that can be passed if required (refer to geemap documentation for details): 
        -resampling = "near", (use 'bilinear', 'bicubic' for soomothing continous data)
        -dtype = None,
        -overwrite = True,
        -num_threads = None,
        -max_tile_size = None,
        -max_tile_dim = None,
        -shape = None,
        -scale_offset = False,
        -unmask_value = None,
        -crs = None,
        -crs_transform = None,

    Note:
    - Required packages: geemap, geedim and earth-engine
    """

    image_asset_address = str(image_asset_address)
    image = ee.Image(image_asset_address)
    image_prefix = image_asset_address.split("/")[0]
    spatial_resolution = image.projection().nominalScale().getInfo()

    if clip:
        image = image.clip(roi)

    if output_path is None:
        downloads_dir = str(Path.home() / "Downloads")
        output_path = os.path.join(downloads_dir, f"{image_prefix}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.tif")
    else:
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    return geemap.download_ee_image(
        image = image,
        filename = output_path,
        region = roi,
        scale = spatial_resolution,
        **kwargs
        )

def download_image_collection(
        collection_asset_address, 
        start_date, 
        end_date, 
        output_path=None, 
        roi=ee.FeatureCollection("projects/ee-joshisur231/assets/pa_effectiveness/nepal_boundary").geometry(), 
        clip=True,
        **kwargs
        ):
    """
    Downloads images in from an Earth Engine image collection.

    Parameters:
    - collection_asset_address (str): A link to the image collection in Earth Engine.
    - start_date (str): Start date in 'YYYY-MM-DD' format.
    - end_date (str): End date in 'YYYY-MM-DD' format.
    - output_path (str, optional): The file path to save the downloaded GeoTIFF image. If None, downloads to the Downloads directory.
    - roi (ee.FeatureCollection, optional): A region of interest (ROI) specified as an Earth Engine FeatureCollection. Defaults to Nepal Boundary.
    - clip (bool, optional): Whether to clip the image to the specified ROI. Default is True.
    - Optional parameters that can be passed if required (refer to geemap documentation for details): 
        -resampling = "near" (use 'bilinear', 'bicubic' for soomothing continous data),
        -dtype = None,
        -overwrite = True,
        -num_threads = None,
        -max_tile_size = None,
        -max_tile_dim = None,
        -shape = None,
        -scale_offset = False,
        -unmask_value = None,
        -filenames = None,
        -crs = None,
        -crs_transform = None,
    Note:
    - Required packages: geemap, geedim and earth-engine
    """
    def clip(image):
        return image.clip(roi)
    
    image_prefix = collection_asset_address.split("/")[0]
    
    collection_asset_address = str(collection_asset_address)
    image_collection = ee.ImageCollection(collection_asset_address)\
        .filterBounds(roi)\
        .filterDate(start_date, end_date)
    
    spatial_resolution = image_collection.first().projection().nominalScale().getInfo()

    if clip:
        image_collection = image_collection.map(clip)

    if output_path is None:
        downloads_dir = str(Path.home() / "Downloads")
        output_path = os.path.join(downloads_dir, f"{image_prefix}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
    else:
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    return geemap.download_ee_image_collection(
        collection = image_collection,
        out_dir = output_path,
        region = roi,
        scale = spatial_resolution,
        **kwargs
        )

def add_image_to_map(image_path = None, image_assest_address = None, layer_name = None, **kwargs):
    """
    Adds Earth Engine assests vector/images and local rasters to an interactive map.

    Parameters:
    - image_path (str): Path to the local image. Defaults to None.
    - image_assest_address (str): A link to the image in Earth Engine. Defaults to None.
    - layer_name (str): Name for the layer
    Note:
    - Required packages: geemap, geedim and earth-engine, requires xarray for local image
    """
    Map = geemap.Map()

    if image_path:
        Map.add_raster(source = image_path, layer_name = layer_name, **kwargs)
    
    if image_assest_address:
        Map.addLayer(ee_object = ee.Image(image_assest_address), name = layer_name, **kwargs)
    
    return Map
    