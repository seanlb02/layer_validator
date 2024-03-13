import os

from flask import Flask
from flask import flash, request, redirect, url_for, send_from_directory
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
    Layer_folder = os.path.join('layer')
    app.config['DOWNLOAD_FOLDER'] = Layer_folder


    ALLOWED_EXTENSIONS = {'zip', 'shp', 'cpg', 'prj', '.sbn', '.shx', '.xml', '.qmd', '.qix', 'sbx', 'kmz'}
    
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
        example = os.path.join(app.config['UPLOAD_FOLDER'], 'folder.png')
        if request.method == 'POST':
            try:
                warning = ""
                # retrieve the file sent via post request (the 'input' element name is data_zip_file)
                file = request.files['data_zip_file']
                # result dicts get stored in this list to be iterated in the html table via jinja
                res_list = []


                # Sanitize first input (.zip)
                if file and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                    file_like_object = file.stream._file  
                    data = file_like_object.read()
                    zipfile_ob = zipfile.ZipFile(file_like_object)
                    file_names = zipfile_ob.namelist()
                    # Sanitize files WITHIN the zip folder
                    for item in file_names: 
                        try:
                            if item.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                                raise fiona.errors.DriverError
                        except:
                                raise fiona.errors.DriverError
                        else:
                            with ZipMemoryFile(data) as zip:
                                for shapefile in file_names:
                                     if shapefile.rsplit('.', 1)[1].lower() == 'shp':
                                        res_item = {}
                                        layer_name = shapefile[:-4]
                                        geometry = ""
                                        projection = ""
                                        corr_file = ""
                                        no_attr = ""
                                        geo_err = ""
                                        topo_err = ""
                                        # with zip.open(f'{file_names[0][:-4]}.shp') as collection:
                                        try:
                                            with zip.open(f'{shapefile}') as collection:
                                                gdf = gpd.GeoDataFrame.from_features([feature for feature in collection], crs=collection.crs)
                                            gdf.sindex
                                            geometry = str(gdf.geom_type[0])
                                            projection = gdf.crs.name
                                        except:
                                            return render_template('corrupt.html', result = res_list, logo = full_filename, folder = example, flavicon = flav)

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
                                        res_list = [*res_list, [layer_name, geometry, projection, corr_file, no_attr, geom_error, topo_error]]
                            flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
                            # return render_template('result.html', layer_name = file.filename[:-4], Warning = warning, geometry = str(gdf.geom_type[0]), projection = gdf.crs.name, corrupt = corr_file, attributes = no_attr, geo_err = geom_error, overlap = topo_error,  logo = full_filename, list = file_names, flavicon = flav)
                            return render_template('result.html', result = res_list, logo = full_filename, flavicon = flav)
                
            except fiona.errors.DriverError: 
                flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
                return render_template('error.html', result = res_list, logo = full_filename, folder = example, flavicon = flav)

                   
        # if request.method == 'GET':
        flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
        return render_template('home.html', logo = full_filename, flavicon = flav)

    @app.route('/transform', methods=['GET', 'POST'])
    def transform_file():
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGCLOGO.png')
        if request.method == 'POST':
            try:
                # retrieve the file sent via post request (the 'input' element name is data_zip_file)
                file = request.files['data_zip_file']
                # result dicts get stored in this list to be iterated in the html table via jinja
                res_list = []
                # Sanitize first input (.zip)
                if file and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                    file_like_object = file.stream._file  
                    data = file_like_object.read()
                    zipfile_ob = zipfile.ZipFile(file_like_object)
                    file_names = zipfile_ob.namelist()
                    # Sanitize files WITHIN the zip folder
                    for item in file_names: 
                        try:
                            if item.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                                raise fiona.errors.DriverError
                        except:
                                raise fiona.errors.DriverError
                        else:
                            with ZipMemoryFile(data) as zip:
                                for spatialfile in file_names:
                                     if spatialfile.rsplit('.', 1)[1].lower() == 'kmz':
                                        res_item = {}
                                        layer_name = spatialfile[:-4]
                                         # with zip.open(f'{file_names[0][:-4]}.shp') as collection:
                                        with zip.open(f'{spatialfile}', allow_unsupported_drivers=True) as collection:
                                            gdf = gpd.GeoDataFrame.from_features([feature for feature in collection], crs=collection.crs)
                                            gdf.to_file(os.path.join(app.config['UPLOAD_FOLDER'], f'{ spatialfile[:-4]}.shp'), driver='ESRI Shapefile')
                                            # return render_template('')
                                            # return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=f'{layer_name}.shp', as_attachment=True)
            except fiona.errors.DriverError: 
                flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
                return render_template('conerror.html', result = res_list, logo = full_filename, flavicon = flav)
        # if request.method == 'GET':
        flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
        return render_template('convert.html', logo = full_filename, flavicon = flav)

    @app.route('/download')
    def download_file(filename):
        return send_from_directory(directory=app.config['DOWNLOAD_FOLDER'], filename='JAPAN.shp', as_attachment=True)


    return app

 
if __name__ == "__main__":
    app.run()
  