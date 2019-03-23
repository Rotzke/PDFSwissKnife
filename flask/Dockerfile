FROM python:3.6
COPY . /code
WORKDIR /code
RUN apt update && apt install -y imagemagick tesseract-ocr tesseract-ocr-eng tesseract-ocr-spa ghostscript
RUN mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xmlout
RUN pip install flask Flask-WTF requests
CMD python app.py
