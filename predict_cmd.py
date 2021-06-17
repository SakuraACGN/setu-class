import predict as p
import sys

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		trained_model = p.cfg.TRAINED_MODEL
		model_name = p.cfg.model_name
		p.imgs = sys.argv[1:]

		# _id, pred_list = tta_predict(trained_model)
		_id, pred_list = p.predict(trained_model)

		submission = p.pd.DataFrame({"ID": _id, "Label": pred_list})
		print(submission.to_string())
