from classify import init_model, predict_url, predict_files
from config import TRAINED_MODEL
import pandas as pd
import sys

if __name__ == "__main__":
	if len(sys.argv) >= 3:
		init_model(TRAINED_MODEL)
		if sys.argv[1] == "url":
			print(predict_url(sys.argv[2]))
		elif sys.argv[1] == "imgs":
			_id, pred_list = predict_files(sys.argv[2:])
			submission = pd.DataFrame({"ID": _id, "Label": pred_list})
			print(submission.to_string())
