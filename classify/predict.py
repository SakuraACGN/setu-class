# -*- coding:utf-8 -*-
# @time :2019.03.15
# @IDE : pycharm
# @author :lxztju
# @github : https://github.com/lxztju

from io import BytesIO
from flask import config
import torch
import os
from PIL import Image
from tqdm import tqdm
from collections import Counter
from config import cfg
from data import tta_test_transform, get_test_transform
from urllib3 import PoolManager

model = ""
pool = PoolManager()

def init_model(m):
	global model
	# 读入模型
	model = load_checkpoint(m)
	print('..... Finished loading model! ......')
	##将模型放置在gpu上运行
	if torch.cuda.is_available(): m.cuda()

def load_checkpoint(filepath):
	checkpoint = torch.load(filepath)
	model = checkpoint['model']  # 提取网络结构
	model.load_state_dict(checkpoint['model_state_dict'])  # 加载网络权重参数
	for parameter in model.parameters():
		parameter.requires_grad = False
	model.eval()
	return model

def predict_files(imgs):
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

def tta_predict_files(imgs):
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

def predict_url(url):
	global model, pool
	r = pool.request('GET', url, preload_content=False)
	d = r.read()
	with Image.open(BytesIO(d)).convert('RGB') as img:
		imgt = get_test_transform(size=cfg.INPUT_SIZE)(img).unsqueeze(0)
		if torch.cuda.is_available(): imgt = imgt.cuda()
		with torch.no_grad(): out = model(imgt)
		r.release_conn()
		if img.format != "WEBP":
			converted = BytesIO()
			img.save(converted, "WEBP")
			converted.seek(0)
			d = converted.read()
		return int(torch.argmax(out, dim=1).cpu().item()), d

def predict_data(dataio):
	with Image.open(dataio).convert('RGB') as img:
		img = get_test_transform(size=cfg.INPUT_SIZE)(img).unsqueeze(0)
		if torch.cuda.is_available(): img = img.cuda()
		with torch.no_grad(): out = model(img)
		return int(torch.argmax(out, dim=1).cpu().item())