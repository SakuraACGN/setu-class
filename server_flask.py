#!/usr/bin/env python3
from base14.base14 import init_dll_in
from gevent import pywsgi
from flask import Flask, request
from urllib.request import unquote, quote
import sys, os
from base14 import init_dll_in
from classify import init_model, predict_url
# from classify import predict_data
from config import TRAINED_MODEL_NOR, TRAINED_MODEL_ERO
from io import BytesIO
from img import get_dhash_b14, save_img

app = Flask(__name__)
MAXBUFFSZ = 16*1024*1024
img_dir = ""
invalid_img_dir = ""
valid_api_list = ["https://api.pixivweb.com/anime18r.php?return=img"]

def get_arg(key: str) -> str:
	return request.args.get(key)

@app.route("/dice", methods=['GET'])
def dice() -> dict:
	global img_dir
	loli = get_arg("loli") == "true"
	url = "" if loli else unquote(get_arg("url"))
	noimg = get_arg("noimg") == "true"
	newcls = get_arg("class") == 9
	c, d = predict_url(url, loli, newcls)
	if len(d) > 0:
		dh = get_dhash_b14(d)
		if loli or url in valid_api_list:
			r = save_img(d, img_dir)
			if r["stat"] == "exist": dh = r["img"]
		else: save_img(d, invalid_img_dir)
		if noimg: return {"img": dh, "class": c}
		else: return d, 200, {"Content-Type": "image/webp", "Class": c, "DHash": quote(dh)}

'''
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
'''

def flush_io() -> None:
	sys.stdout.flush()
	sys.stderr.flush()

def handle_client():
	global img_dir, invalid_img_dir
	host = sys.argv[1]
	port = int(sys.argv[2])
	img_dir = sys.argv[3]
	invalid_img_dir = sys.argv[4]
	if img_dir[-1] != '/': img_dir += "/"
	if invalid_img_dir[-1] != '/': invalid_img_dir += "/"
	print("Starting SC at:", host, port)
	init_dll_in('/usr/local/lib/')
	init_model(TRAINED_MODEL_NOR, TRAINED_MODEL_ERO)
	pywsgi.WSGIServer((host, port), app).serve_forever()

if __name__ == '__main__':
	if len(sys.argv) == 5:
		if os.fork() == 0:		#创建daemon
			os.setsid()
			#创建孙子进程，而后子进程退出
			if os.fork() > 0: sys.exit(0)
			#重定向标准输入流、标准输出流、标准错误
			flush_io()
			si = open("/dev/null", 'r')
			so = open("./log.txt", 'w')
			se = open("./log_err.txt", 'w')
			os.dup2(si.fileno(), sys.stdin.fileno())
			os.dup2(so.fileno(), sys.stdout.fileno())
			os.dup2(se.fileno(), sys.stderr.fileno())
			pid = os.fork()
			while pid > 0:			#监控服务是否退出
				#signal(SIGCHLD, SIG_IGN)
				#signal(SIGPIPE, SIG_IGN)		# 忽略管道错误
				os.wait()
				print("Subprocess exited, restarting...")
				pid = os.fork()
			if pid < 0: print("Fork error!")
			else: handle_client()
		else: print("Creating daemon...")
	else: print("Usage: <host> <port> <valid_img_save_dir> <invalid_img_save_dir>")
