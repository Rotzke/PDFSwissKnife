import os
import subprocess

from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from search_client import search_term
from werkzeug.utils import secure_filename

# App config.
DEBUG = True
UPLOAD_FOLDER = '/books/tmp'
ALLOWED_EXTENSIONS = ['pdf']
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ReusableForm(Form):
    search = TextField('Search term:', validators=[validators.required()])
    title = TextField('Title:')


@app.route("/", methods=['GET', 'POST'])
def search():
    form = ReusableForm(request.form)
    results = False
    if request.method == 'POST':
        search = request.form['search']
        title = request.form['title']

        if form.validate():
            results = search_term(search, title)
            if not results:
                flash('Error: No results found!')
            else:
                flash('Please see search results below')
        else:
            flash('Error: Please enter a search term!')
    return render_template('search.html', form=form, results=results)


@app.route("/ocr", methods=['GET', 'POST'])
def ocr():
    form = ReusableForm(request.form)
    results = False
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('Error: No file part!')
        else:
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('Error: No selected file!')
            else:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    subprocess.check_output(["convert -limit memory 2GiB -limit map 4GiB -density 300 /books/tmp/{0} -depth 8 -strip -background white -alpha off /books/tmp/{0}.png".format(filename)],
                                            shell=True)
                    subprocess.check_output([f"for i in `ls /books/tmp/ | grep '{filename}.*png'`;do tesseract /books/tmp/$i -l eng+spa /books/$i;done"],
                                            shell=True)
                    flash(f'The file {filename} was processed')
                else:
                    flash('Error: You may upload only PDF files!')
    return render_template('ocr.html', form=form, results=results)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
