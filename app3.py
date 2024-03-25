import replicate

training = replicate.trainings.create(
  version= "meta/llama-2-7b-chat:13c3cdee13ee059ab779f0291d29054dab00a47dad8261375654de5540165fb0",
  input={
    "train_data": "https://sengotbuc.s3.eu-north-1.amazonaws.com/train_data.jsonl",
    "num_train_epochs": 3
  },
  destination="adefolasayo/sengbot"
)

print(training)