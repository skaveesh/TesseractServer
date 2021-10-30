from skimage import io
import cv2
import numpy as np
import pytesseract
import socketserver
import http.server
from urllib.parse import unquote
import urllib
import urllib.request 

PORT = 8800

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\skaveesh\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def url_to_image(url, readFlag=cv2.IMREAD_COLOR):
        page=urllib.request.Request(url,headers={'User-Agent': 'Mozilla/5.0'}) 
        resp = urllib.request.urlopen(page)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, readFlag)
        return image


class ServerHandler(http.server.SimpleHTTPRequestHandler):
        def do_OPTIONS(self):
                self.send_response(200, "ok")
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET,HEAD,OPTIONS,POST,PUT')
                self.send_header('Access-Control-Allow-Headers', 'Access-Control-Allow-Headers,access-control-allow-origin,access-control-allow-methods')
                self.end_headers()
        
        def do_POST(self):
                self.data_string = self.rfile.read(int(self.headers['Content-Length'])).decode("utf-8")

                if(self.data_string.startswith('imgUrlToParse=')):
                        url = unquote(self.data_string.partition('&')[0].partition('=')[-1])

                        print("Image Location", url)

                        # Download the image from the URL and convert into image Object
                        image = url_to_image(url)

                        # OpenCV - turning the image into grayscale image
                        grayscaledMat = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                        
                        # OpenCV - all pixels value above 120 will be set to 255. Then invert it
                        retval, thresholdMat = cv2.threshold(grayscaledMat, 120, 255,  cv2.THRESH_BINARY_INV)

                        # OpenCV - inverting the image with bitwise_not operator
                        invertedMat = cv2.bitwise_not(thresholdMat)

                        # Show the image if showProcessedImage key is true
                        if(self.data_string.partition('&')[2] == 'showProcessedImage=true'):
                                cv2.imshow('Final MAT', invertedMat)
                                cv2.waitKey()

                        # Processing the image with tesseract OCR
                        data = pytesseract.image_to_string(invertedMat, config='-l eng --psm 8 --oem 3 --dpi 300 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ" -c page_separator=""')
                        
                        print("Image response", data)
                        
                        self.send_response(200, "ok")
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Access-Control-Allow-Methods', 'OPTIONS,POST')
                        self.send_header('Access-Control-Allow-Headers', 'Access-Control-Allow-Headers,access-control-allow-origin,access-control-allow-methods')
                        self.end_headers()
                        self.wfile.write(data.encode(encoding='utf_8'))
                else:
                        self.send_response(400, "bad-request")
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Access-Control-Allow-Methods', 'OPTIONS,POST')
                        self.send_header('Access-Control-Allow-Headers', 'Access-Control-Allow-Headers,access-control-allow-origin,access-control-allow-methods')
                        self.end_headers()


Handler = ServerHandler

httpd = socketserver.TCPServer(("", PORT), Handler)

print("Serving at port", PORT)
httpd.serve_forever()
