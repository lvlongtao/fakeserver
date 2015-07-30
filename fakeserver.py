import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response
from werkzeug import secure_filename
import StringIO
import datetime, time
import json
import zipfile
import gzip
import base64

# Initialize the Flask application
app = Flask(__name__, static_url_path="")

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET'])
def list():
    filenames = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('upload.html', filenames=filenames)


@app.route('/commandURL', methods=['POST'], endpoint='get_command')
def get_command():
    headers = request.headers
    print '|'
    print '|'
    print '| Command'
    print '|'
    print '|'
    print headers
    print request.remote_addr
    zf = zipfile.ZipFile(StringIO.StringIO(request.data))
    print zf.namelist()
    for name in zf.namelist():
        fp = zf.open(name)
        msg = fp.read()
        print msg
        now = datetime.datetime.now()
        nowstr = now.strftime("%Y-%m-%d_%H:%M:%S")
        filename = app.config['UPLOAD_FOLDER'] + request.remote_addr + '_' + nowstr + '_' + name
        f = open(filename,'w+')
        f.write(msg)
        f.close()
    """
    ret = json.dumps('{"timestamp":1437631602141,"identityInfo":"1,33cb4599-1f15-4fef-866f-330f58df80ce,4,0237107f-59f2-4c37-9669-269e5a4e2429","commands":[]}')
    z = zipfile.ZipFile(u'test.zip', mode='w')
    fzip = open(u'manifest.json','w')
    fzip.write(ret)
    fzip.close()
    z.write(u'manifest.json')
    print '=================================='
    print z.namelist()
    qq = z.open(u'manifest.json')
    print qq.read()
    """
    #response = Response(z, mimetype='application/zip')
    response = Response('OK')
    response.status_code = 200
    return response


@app.route('/eventURL', methods=['POST'])
def get_event():
    headers = request.headers
    print '|'
    print '|'
    print '| Event'
    print '|'
    print '|'
    print headers
    print request.remote_addr
    gzip_buffer = StringIO.StringIO(request.data)
    gzip_file = gzip.GzipFile(fileobj=gzip_buffer)
    msg = gzip_file.read()
    gzip_file.close()
    print msg
    now = datetime.datetime.now()
    nowstr = now.strftime("%Y-%m-%d_%H:%M:%S")
    filename = app.config['UPLOAD_FOLDER'] + request.remote_addr + '_' + nowstr + '_' + 'event.json'
    f = open(filename,'w+')
    f.write(msg)
    f.close()

    response = Response('OK')
    response.status_code = 200
    return response

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded files
    uploaded_files = request.files.getlist('file[]')
    print uploaded_files
    filenames = []
    for file in uploaded_files:
        # Check if the file is one of the allowed types/extensions
    #print allowed_file(file.filename)
    #print file.filename
    #if file and allowed_file(file.filename):
    # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        print filename
    # Move the file form the temporal folder to the upload
    # folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # Save the filename into a list, we'll use it later
        filenames.append(filename)
    # Redirect the user to the uploaded_file route, which
    # will basicaly show on the browser the uploaded file
    # Load an html page with a link to each uploaded file
    return render_template('upload.html', filenames=filenames)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)



if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("5000"),
        debug=True
    )
