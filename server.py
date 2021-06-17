#!/usr/bin/env python3
from base14.base14 import init_dll_in
from gevent import pywsgi
from flask import Flask, request
from urllib.request import unquote, quote
import sys, os
from base14 import init_dll_in
from classify import init_model, predict_data, predict_url
from config import TRAINED_MODEL
from io import BytesIO
from img import get_dhash_b14, save_img

app = Flask(__name__)
MAXBUFFSZ = 16*1024*1024

init_dll_in('/usr/local/lib/')
init_model(TRAINED_MODEL)

def get_arg(key: str) -> str:
	return request.args.get(key)

@app.route("/dice", methods=['GET'])
def dice() -> dict:
	c, d = predict_url(unquote(get_arg("url")))
	if len(d) > 0:
		dh = get_dhash_b14(d)
		save_img(d, img_dir)
		return d, 200, {"Content-Type": "image/webp", "Class": c, "DHash": quote(dh)}

@app.route("/classdat", methods=['POST'])
def upload() -> dict:
		length = int(request.headers.get('Content-Length'))
		print("准备接收:", length, "bytes")
		if length < MAXBUFFSZ:
			data = request.get_data()
			return {"img": get_dhash_b14(data), "class": predict_data(BytesIO(data))}
		else:
			data = request.stream.read(length)
			return {"img": get_dhash_b14(data), "class": predict_data(BytesIO(data))}

@app.route("/classform", methods=['POST'])
def upform() -> dict:
	re = []
	for f in request.files.getlist("img"):
		re.append({"name":f.filename, "img": get_dhash_b14(f), "class": predict_data(f)})
	return {"result": re}

@app.before_first_request
def setuid() -> None:
	if server_uid > 0:		#监听后降权
		os.setuid(server_uid)

if __name__ == '__main__':
	if len(sys.argv) == 4 or len(sys.argv) == 5:
		host = sys.argv[1]
		port = int(sys.argv[2])
		img_dir = sys.argv[3]
		if img_dir[-1] != '/': img_dir += "/"
		server_uid = int(sys.argv[4]) if len(sys.argv) == 5 else 0
		print("Starting SC at:", host, port)
		pywsgi.WSGIServer((host, port), app).serve_forever()
	else: print("Usage: <host> <port> <img_dir> (server_uid)")
