# TesseractServer
Tesseract text OCR Server Written in Python

curl command:
```
curl --location --request POST 'http://localhost:8800' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'imgUrlToParse=https://i.imgur.com/OJUt4Kc.png' \
--data-urlencode 'showImage=true'
```
