from flask import Flask, render_template, request, redirect, url_for
from translatevideo import translate
import boto3
from pathlib import Path
app = Flask(__name__)


def upload(file_name, bucket, object_name=None):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, 'uploads/{}'.format(file_name))
        location = boto3.client('s3').get_bucket_location(Bucket=bucket)['LocationConstraint']
        #url = "https://s3-"+location+".amazonaws.com/"+bucket+"/"+'uploads/{}'.format(file_name)
        url = "https://mybucket-ccl-1234.s3.amazonaws.com/uploads/"+file_name
    except ClientError as e:
        logging.error(e)
        return False
    return url


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/translate', methods=['POST'])
def translateVideo():
    if request.method == 'POST':
        file = request.files['fileUpload']
        language = request.form['language']
        # save file to local directory
        file.save(file.filename)
        url = upload(file.filename, 'mybucket-ccl-1234')
        # translate(file.filename, url, 'mp4', ['en', 'de'])
        Path(file.filename.split(".")[0]+"-en.mp4").rename("static/"+file.filename)
        Path(file.filename.split(".")[0]+"-"+language+".mp4").rename("static/"+file.filename.split(".")[0]+"-"+language+".mp4")
        return render_template('translate.html',file=file.filename, file_translated=file.filename.split(".")[0]+"-"+language+".mp4", language=language)


if __name__ == '__main__':
    app.run(debug=True)
