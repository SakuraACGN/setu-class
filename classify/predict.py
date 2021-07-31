# -*- coding:utf-8 -*-
# @time :2019.03.15
# @IDE : pycharm
# @author :lxztju
# @github : https://github.com/lxztju

from io import BytesIO
import torch
import os
from PIL import Image
# from tqdm import tqdm
from collections import Counter
from config import cfg
from data import get_test_transform
# from data import tta_test_transform
from urllib3 import PoolManager
from time import time

model = ""
moder = ""
pool = PoolManager()

def init_model(nor, ero) -> None:
	global model, moder
	# 读入模型
	model = load_checkpoint(nor)
	moder = load_checkpoint(ero)
	print('..... Finished loading model! ......')
	##将模型放置在gpu上运行
	if torch.cuda.is_available(): m.cuda()

def load_checkpoint(filepath: str):
    	checkpoint = torch.load(filepath) if torch.cuda.is_available() else torch.load(filepath, map_location=torch.device('cpu'))
	model = checkpoint['model']  # 提取网络结构
	model.load_state_dict(checkpoint['model_state_dict'])  # 加载网络权重参数
	for parameter in model.parameters():
		parameter.requires_grad = False
	model.eval()
	return model

'''
def predict_files(imgs: list):
	global model
	pred_list, _id = [], []
	for i in tqdm(range(len(imgs))):
		img_path = imgs[i].strip()
		# print(img_path)
		_id.append(os.path.basename(img_path).split('.')[0])
		with Image.open(img_path).convert('RGB') as img:
			# print(type(img))
			img = get_test_transform(size=cfg.INPUT_SIZE)(img).unsqueeze(0)
			if torch.cuda.is_available(): img = img.cuda()
			with torch.no_grad(): out = model(img)
			prediction = torch.argmax(out, dim=1).cpu().item()
			pred_list.append(prediction)
	return _id, pred_list

def tta_predict_files(imgs: list):
	global model
	pred_list, _id = [], []
	for i in tqdm(range(len(imgs))):
		img_path = imgs[i].strip()
		# print(img_path)
		_id.append(os.path.basename(img_path).split('.')[0])
		with Image.open(img_path).convert('RGB') as img1:
			# print(type(img))
			pred = []
			for i in range(8):
				img = tta_test_transform(size=cfg.INPUT_SIZE)(img1).unsqueeze(0)
				if torch.cuda.is_available(): img = img.cuda()
				with torch.no_grad(): out = model(img)
				prediction = torch.argmax(out, dim=1).cpu().item()
				pred.append(prediction)
			res = Counter(pred).most_common(1)[0][0]
			pred_list.append(res)
	return _id, pred_list
'''

last_req_time = 0
def clear_pool() -> None:
	global pool, last_req_time
	if time() - last_req_time > 60:
		pool.clear()
		last_req_time = time()

LOLI_API_URL = "https://api.lolicon.app/setu/v2?r18=2&proxy=null"
def get_loli_url() -> str:
	global pool
	r = pool.request('GET', LOLI_API_URL, preload_content=False)
	print("Get request.")
	d = r.read().decode()
	r.release_conn()
	d = d[d.index("\"urls\":{\"original\":\"")+20:]
	d = d[:d.index("\"}")]
	return d

def predict_url(url: str, loli: bool, newcls: bool):
	global model, pool
	clear_pool()
	r = pool.request('GET', get_loli_url() if loli else url, headers={"Referer":"https://www.pixiv.net"} if loli else None, preload_content=False)
	print("Get request.")
	d = r.read()
	r.release_conn()
	print("Read success.")
	with Image.open(BytesIO(d)).convert('RGB') as img:
		imgt = get_test_transform(size=cfg.INPUT_SIZE)(img).unsqueeze(0)
		if torch.cuda.is_available(): imgt = imgt.cuda()
		with torch.no_grad():
			out = model(imgt)
			oue = moder(imgt)
		if img.format != "WEBP":
			converted = BytesIO()
			img.save(converted, "WEBP")
			converted.seek(0)
			d = converted.read()
			print("Convert success.")
		n = int(torch.argmax(out, dim=1).cpu().item())
		e = int(torch.argmax(oue, dim=1).cpu().item())
		if newcls:
			if n > 3 and n < 6 and e > 4: p = 6 if e == 5 else 8
			else: p = n
		elif e > 4 and n < 4: p = n
		else: p = e
		return p, d

'''
def predict_data(dataio) -> int:
	with Image.open(dataio).convert('RGB') as img:
		img = get_test_transform(size=cfg.INPUT_SIZE)(img).unsqueeze(0)
		if torch.cuda.is_available(): img = img.cuda()
		with torch.no_grad():
			out = model(img)
			oue = moder(img)
		n = int(torch.argmax(out, dim=1).cpu().item())
		e = int(torch.argmax(oue, dim=1).cpu().item())
		if n > 3 and n < 6 and e > 4: p = 6 if e == 5 else 8
		else: p = n
		return p
'''