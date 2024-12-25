import argparse
from scripts import scrape_data, preprocess_data, train_model, predict

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FIFA Predictor")
    parser.add_argument("--task", type=str, required=True, help="Task to run: scrape, preprocess, train, predict")

    args = parser.parse_args()

    if args.task == "scrape":
        scrape_data.main()
    elif args.task == "preprocess":
        preprocess_data.main()
    elif args.task == "train":
        train_model.main()
    elif args.task == "predict":
        predict.main()
    else:
        print("Invalid task. Choose from: scrape, preprocess, train, predict.")
