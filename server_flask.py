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
server_uid = 0
img_dir = ""
save_image = False

def get_arg(key: str) -> str:
	return request.args.get(key)

@app.route("/dice", methods=['GET'])
def dice() -> dict:
	global img_dir
	c, d = predict_url(unquote(get_arg("url")))
	if len(d) > 0:
		dh = get_dhash_b14(d)
		if save_image:
			save_img(d, img_dir)
			print("Save success.")
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
	global server_uid
	if server_uid > 0:		#监听后降权
		os.setuid(server_uid)

def flush_io() -> None:
	sys.stdout.flush()
	sys.stderr.flush()

def handle_client():
	global server_uid, img_dir, save_image
	host = sys.argv[1]
	port = int(sys.argv[2])
	save_image = sys.argv[3] == "true"
	if save_image:
		img_dir = sys.argv[4]
		if img_dir[-1] != '/': img_dir += "/"
	else: server_uid = int(sys.argv[4])
	print("Starting SC at:", host, port)
	init_dll_in('/usr/local/lib/')
	init_model(TRAINED_MODEL)
	pywsgi.WSGIServer((host, port), app).serve_forever()

if __name__ == '__main__':
	if len(sys.argv) == 4:
		'''
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
		'''
		handle_client()
	else: print("Usage: <host> <port> <save_img:true/false> (img_dir/server_uid)")