# -*- coding:utf-8 -*-
# @time :2019.03.15
# @IDE : pycharm
# @author :lxztju
# @github : https://github.com/lxztju

from io import BytesIO
import torch
import os
from PIL import Image
from tqdm import tqdm
from collections import Counter
from config import cfg
from data import get_test_transform
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

def predict_files(imgs: list):
	global model, moder
	pred_list, _id = [], []
	for i in tqdm(range(len(imgs))):
		img_path = imgs[i].strip()
		# print(img_path)
		_id.append(os.path.basename(img_path).split('.')[0])
		with Image.open(img_path).convert('RGB') as img:
			# print(type(img))
			img = get_test_transform(size=cfg.INPUT_SIZE)(img).unsqueeze(0)
			if torch.cuda.is_available(): img = img.cuda()
			with torch.no_grad():
				out = model(img)
				oue = moder(img)
			n = int(torch.argmax(out, dim=1).cpu().item())
			e = int(torch.argmax(oue, dim=1).cpu().item())
			p = n
			pred_list.append(p + n * 10 + e * 100)
	return _id, pred_list

last_req_time = 0
def clear_pool() -> None:
	global pool, last_req_time
	if time() - last_req_time > 60:
		pool.clear()
		last_req_time = time()

LOLI_API_URL_R18 = "https://api.lolicon.app/setu/v2?r18=2&proxy=null"
LOLI_API_URL_NORM = "https://api.lolicon.app/setu/v2?proxy=null"
def get_loli_url(withr18: bool):
	global pool
	r = pool.request('GET', LOLI_API_URL_R18 if withr18 else LOLI_API_URL_NORM, preload_content=False)
	print("Get request.")
	d = r.read().decode()
	r.release_conn()
	r = d.index("\"r18\":")
	r = d[r+6:r+10] == "true"
	d = d[d.index("\"urls\":{\"original\":\"")+20:]
	d = d[:d.index("\"}")]
	return d, r

def predict_url(url: str, loli: bool, newcls: bool, withr18: bool, nopredict: bool):
	global model, moder, pool
	clear_pool()
	if loli: url, r18 = get_loli_url(withr18)
	else: r18 = False
	r = pool.request('GET', url, headers={"Referer":"https://www.pixiv.net"} if loli else None, preload_content=False)
	print("Get request.")
	d = r.read()
	r.release_conn()
	print("Read success.")
	with Image.open(BytesIO(d)).convert('RGB') as img:
		imgt = get_test_transform(size=cfg.INPUT_SIZE)(img).unsqueeze(0)
		if not nopredict:
			if torch.cuda.is_available(): imgt = imgt.cuda()
			with torch.no_grad():
				out = model(imgt)
				if not newcls: oue = moder(imgt)
		if img.format != "WEBP":
			converted = BytesIO()
			img.save(converted, "WEBP")
			converted.seek(0)
			d = converted.read()
			print("Convert success.")
		if nopredict: p = 0
		else:
			n = int(torch.argmax(out, dim=1).cpu().item())
			if not newcls:
				p = int(torch.argmax(oue, dim=1).cpu().item())
				if p > 2 and n < 3: p = n
			else: p = n
		if loli:
			if r18:
				if newcls:
					if p < 6: p = 8
				elif p < 5: p = 6
			else:
				if newcls:
					if p > 5: p = 5
				else:
					if p > 4: p = 4
		return p, d

'''
def predict_data(dataio) -> int:
	global model, moder
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