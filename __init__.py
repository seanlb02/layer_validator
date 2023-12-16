import os

from flask import Flask
from flask import flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import zipfile
from flask import render_template
import geopandas as gpd
import io
from fiona.io import ZipMemoryFile
import fiona
import tempfile
from fiona.io import ZipMemoryFile
import zipfile
import copy


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    IMAGE_FOLDER = os.path.join('static')
    app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

    ALLOWED_EXTENSIONS = {'zip', 'shp', 'cpg', 'prj', '.sbn', '.shx', '.xml', '.qmd', '.qix', 'sbx'}
    
    TEMP = tempfile.gettempdir()
    app.config['TEMP_FOLDER'] = TEMP


    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

                        #     filename = secure_filename(file.filename)
                #     # Set up a place to put the upload in temp
                #     path = (os.path.join(app.config['TEMP_FOLDER'], filename))
                #     # this check_zip function is messing everything up
                #     # check_zip(file)
                #     file.save(path)
                #     # Create the geodataframe and set up a spatial index:
                #     gdf = gpd.read_file(str(path))
                #     gdf.sindex

        

    #Simple form input on webpage route
    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGCLOGO.png')
        if request.method == 'POST':
            try:
                warning = ""
                # retrieve the file sent via post request (the 'input' element name is data_zip_file)
                file = request.files['data_zip_file']
                


                # Sanitize first input (.zip)
                if file and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                    file_like_object = file.stream._file  
                    data = file_like_object.read()
                    zipfile_ob = zipfile.ZipFile(file_like_object)
                    file_names = zipfile_ob.namelist()
                    # Sanitize files WITHIN the zip folder
                    for item in file_names: 
                        if item.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                            raise fiona.errors.DriverError
                        else:
                            with ZipMemoryFile(data) as zip:
                                with zip.open(f'{file.filename[:-4]}.shp') as collection:
                                    gdf = gpd.GeoDataFrame.from_features([feature for feature in collection], crs=collection.crs)
                            gdf.sindex
                            # geom err check:
                            if False in gdf.is_valid.values:
                                geom_error = "Yes"
                            else: 
                                geom_error = "No"
                            # corrupt geometry check:
                            corr_file = ""
                            if True in gdf.is_empty.values:
                                corr_file = "Yes"
                            else:
                                corr_file= "No"
                            # empty attribute table:
                            if gdf.shape[1] >= 4:
                                no_attr = "Present"
                            else:
                                no_attr = "None"
                            # Topology check
                            # We only check Topology/Geometry errors for polygons and multilines
                            if 'Point' in gdf.geom_type:
                                pass
                            else:
                                # new dummy dataframe to host any overlapping layers
                                sdf = gdf.sindex.query(gdf.geometry, predicate='overlaps')
                                # if there are any:
                                if sdf.size != 0:
                                    topo_error = "Yes"
                                else:
                                    topo_error = "No"
                            flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
                            return render_template('result.html', layer_name = file.filename[:-4], Warning = warning, geometry = str(gdf.geom_type[0]), projection = gdf.crs.name, corrupt = corr_file, attributes = no_attr, geo_err = geom_error, overlap = topo_error,  logo = full_filename, list = file_names, flavicon = flav)

                
            except fiona.errors.DriverError: 
                pass

                   
        # if request.method == 'GET':
        flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
        return render_template('home.html', logo = full_filename, flavicon = flav)
    return app

 
if __name__ == "__main__":
    app.run()
  