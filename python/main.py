import subprocess
import json
import os
import sys

OGR2OGR_PATH = "C:\\OSGeo4W\\bin\\ogr2ogr.exe"
INPUT_DATA = "inputData.gpkg"

if __name__ == "__main__":
    # Get parameters file path from command line argument
    parameters_file = sys.argv[1]

    # Read and parse the parameters.json file
    with open(parameters_file, "r", encoding="utf-8") as json_file:
        parameters = json.load(json_file)

    # Reproject the parameters.json to business data CRS (EPSG:2056)
    # and save it as a temporary clipper.geojson file in FolderOut
    cmd = [
        OGR2OGR_PATH,
        "-s_srs",
        "EPSG:4326",
        "-t_srs",
        "EPSG:2056",
        os.path.join(parameters["properties"]["FolderOut"], "clipper.geojson"),
        parameters_file,
    ]

    # Run the ogr2ogr command while catching and raising errors
    try:
        subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        print("Processing parameters file failed")
        raise subprocess.CalledProcessError(1, cmd) from e

    # Translate format to OGR format name
    if parameters["properties"]["Parameters"]["FORMAT"] == "GEOJSON":
        format = "GeoJSON"
    elif parameters["properties"]["Parameters"]["FORMAT"] == "GPKG":
        format = "GPKG"
    elif parameters["properties"]["Parameters"]["FORMAT"] == "DXF":
        format = "DXF"

    # Translate Projection to OGR CRS name
    if parameters["properties"]["Parameters"]["PROJECTION"] == "SWITZERLAND95":
        output_proj = "EPSG:2056"
    elif parameters["properties"]["Parameters"]["PROJECTION"] == "SWITZERLAND":
        output_proj = "EPSG:21781"
    else:
        output_proj = "EPSG:2056"

    # Clip, reproject and save the data in FolderOut
    cmd = [
        OGR2OGR_PATH,
        "-s_srs",
        "EPSG:2056",
        "-t_srs",
        output_proj,
        "-clipsrc",
        os.path.join(parameters["properties"]["FolderOut"], "clipper.geojson"),
        "-f",
        format,
        os.path.join(
            parameters["properties"]["FolderOut"],
            f"result.{parameters['properties']['Parameters']['FORMAT'].lower()}",
        ),
        INPUT_DATA,
    ]

    # Run the ogr2ogr command while catching and raising errors
    try:
        subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        print("Processing data failed")
        raise subprocess.CalledProcessError(1, cmd) from e

    # Delete temporary clipper.geojson file
    os.remove(os.path.join(parameters["properties"]["FolderOut"], "clipper.geojson"))

    # Example to deal with an extraction that returns no features (empty).
    # This example only works for the format geojson. To be used with the option
    # "Cancel processing when no data is found" in Extract
    ouput_geojson = os.path.join(
        parameters["properties"]["FolderOut"],
        f"result.{parameters["properties"]["Parameters"]["FORMAT"].lower()}"
    )

    if ouput_geojson.endswith(".geojson"):

        with open(ouput_geojson, "r", encoding="utf-8") as json_file:
            ouput_geojson = json.load(json_file)

        if len(ouput_geojson["features"]) == 0:
            raise Exception("noDataForExtract")

