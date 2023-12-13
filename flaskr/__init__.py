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


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    IMAGE_FOLDER = os.path.join('static')
    app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
    ALLOWED_EXTENSIONS = {'zip'}
    
    folder = 'hi'
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

    #Simple form input on webpage route
    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGCLOGO.png')
        if request.method == 'POST':
            # retrieve the file sent via post request (input name is data_zip_file)
            file = request.files['data_zip_file']
            # files = request.files.to_dict('data_zip_file')
            # for file in files:     #image will be the key 
            #     file_name = files[file].filename
            #     files[file].save(os.path.join(app.config['TEMP_FOLDER'], file))
            # files = request.files.getlist(multi=False, 'data_zip_file')
            # for file in files:
            # files.save(os.path.join(app.config['TEMP_FOLDER'], files.filename)) 
            # for file in uploaded_files:
            #     file.save(os.path.join(app.config['TEMP_FOLDER'], file.filename))
            # file_like_object = file.stream._file  
            # zipfile_ob = zipfile.ZipFile(file_like_object)
            # bytes_buffer = io.BytesIO()
            # content = file.read()
            
            # file_names = zipfile_ob.namelist()
            # for file_name in file_names:
            #     if file_name.endswith(".shp"):
            #         shapefile = file_name
            # with ZipMemoryFile(file_like_object) as zip:
            #     gdf = gpd.read_file(zip)
            
            path = (os.path.join(app.config['TEMP_FOLDER'], file.filename))
            file.save(path)
            gdf = gpd.read_file(str(path))
            # path = os.path.join(app.config['TEMP_FOLDER'], file)
            # gdf = gpd.read_file(rf'{path}')
                    # print(collection.schema)
            # item = zipfile_ob.open(shapefile)
            # files = [(zipfile_ob.open(name).read() for name in file_names)]
            # shape = zipfile_ob.open(shapefile).read()
            
            # if "polygon" in gdf.geom_type:
            return str(gdf.geom_type[0])
                    
        if request.method == 'GET':
            flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
            return render_template('home.html', logo = full_filename, flavicon = flav)
    return app