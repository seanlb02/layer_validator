import os

from flask import Flask
from flask import flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import zipfile
from flask import render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    IMAGE_FOLDER = os.path.join('static')
    app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER
    ALLOWED_EXTENSIONS = {'zip'}
    


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
            file = request.form['data_zip_file']
            file_like_object = file.stream._file  
            zipfile_ob = zipfile.ZipFile(file_like_object)
            print(file_names = zipfile_ob.namelist())
        flav = os.path.join(app.config['UPLOAD_FOLDER'], 'MCGC_AGREEMENT_LOGO-01.jpg')
        return render_template('home.html', logo = full_filename, flavicon = flav)
    return app