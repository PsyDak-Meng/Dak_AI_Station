import os
os.environ["CUDA_VISIBLE_DEVICES"]="0"
import torch
import torch.nn as nn
#import bitsandbytes as bnb
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import json
from transformers import DistilBertForSequenceClassification, AdamW
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter


# LOAD MODEL
model = AutoModelForCausalLM.from_pretrained(
    "bigscience/bloom-7b1",
    device_map='auto',
    load_in_8bit=False
)

tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom-7b1")

# FREEZE ORIGINAL WEIGHTS
for param in model.parameters():
  param.requires_grad = False  # freeze the model - train adapters later
  if param.ndim == 1:
    # cast the small parameters (e.g. layernorm) to fp32 for stability
    param.data = param.data.to(torch.float32)

model.gradient_checkpointing_enable()  # reduce number of stored activations
model.enable_input_require_grads()

class CastOutputToFloat(nn.Sequential):
  def forward(self, x): return super().forward(x).to(torch.float32)

model.lm_head = CastOutputToFloat(model.lm_head)



# SETUP LoRa Adapters
def print_trainable_parameters(model):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    )

def check_to_half(model):
  for param in model.parameters():
    # Check if parameter dtype is  Float (float32)
    if param.dtype == torch.float32:
        param.data = param.data.to(torch.float16)

config = LoraConfig(
    r=16, #attention heads
    lora_alpha=32, #alpha scaling
    # target_modules=["q_proj", "v_proj"], #if you know the
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM" # set this for CLM or Seq2Seq
)

model = get_peft_model(model, config)
check_to_half(model)
print_trainable_parameters(model)



# LOAD DATA
def load_corpus(path):
    json_list = []
    corpus_dict = {}
    with open(path, 'r') as json_file:
        for json_obj in json_file:
            json_dict = json.loads(json_obj)
            json_list.append(json_dict)
    for json_obj in json_list:
        corpus_dict[json_obj["_id"]] = json_obj["title"] + "\n" + json_obj["text"]
    return corpus_dict


def load_query(path):
    json_list = []
    query_dict = {}
    with open(path, 'r') as json_file:
        for json_obj in json_file:
            json_dict = json.loads(json_obj)
            json_list.append(json_dict)
    for json_obj in json_list:
        query_dict[json_obj["_id"]] = json_obj["text"]
    return query_dict


def pad_sequence(n:int, tokens):# 272 & 3325
  pad = torch.zeros((n))
  pad[:len(tokens)] = torch.Tensor(tokens)
  pad = pad.int()
  return pad

class ArxivDataset(Dataset):
    """Arxiv dataset."""

    def __init__(self, tsv_file, query_file, corpus_file):
        """
        Arguments:
            tsv_file (string): Path to the tsv training file.
            query_file: Path to query file
            corpus_file: Path to answers file
        """
        self.tsv = pd.read_csv(tsv_file,sep='\t')
        self.query = load_query(query_file)
        self.corpus = load_corpus(corpus_file)
        self.score = list(self.tsv["score"])

    def __len__(self):
        return len(self.tsv)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        sample = {}
        sample["query"] = pad_sequence(272, tokenizer.encode(self.query[self.tsv.loc[idx,"query-id"]]))
        sample["corpus"] = pad_sequence(3325, tokenizer.encode(self.corpus[str(self.tsv.loc[idx,"corpus-id"])]))

        return sample
    
# TRAINING


device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

train_dataset = ArxivDataset(tsv_file="arxiv-beir-cs-ml-generated-queries/gen-3-qrels/train.tsv",
                             query_file="arxiv-beir-cs-ml-generated-queries/gen-3-queries.jsonl",
                             corpus_file="arxiv-beir-cs-ml-generated-queries/corpus.jsonl")
train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)

loss_fn = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=5e-4, momentum=0.9)

def train_one_epoch(epoch_index, tb_writer, training_loader):
    running_loss = 0.
    last_loss = 0.

    for i, data in enumerate(training_loader):

        inputs, labels = data["query"], data["corpus"]
        print(inputs.type(),labels.type())

        optimizer.zero_grad()
        outputs = model(inputs)

        loss = loss_fn(outputs, labels)
        loss.backward()

        optimizer.step()

        # Gather data and report
        running_loss += loss.item()
        if i % 1000 == 999:
            last_loss = running_loss / 1000 # loss per batch
            print('  batch {} loss: {}'.format(i + 1, last_loss))
            tb_x = epoch_index * len(training_loader) + i + 1
            tb_writer.add_scalar('Loss/train', last_loss, tb_x)
            running_loss = 0.

    return last_loss



# Initializing in a separate cell so we can easily add more epochs to the same run
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
writer = SummaryWriter('runs/fashion_trainer_{}'.format(timestamp))
epoch_number = 0

EPOCHS = 100

best_vloss = 1_000_000.


for epoch in range(EPOCHS):
    print('EPOCH {}:'.format(epoch_number + 1))

    # Make sure gradient tracking is on, and do a pass over the data
    model.train(True)
    avg_loss = train_one_epoch(epoch_number, writer,train_loader)
    print('LOSS train {}'.format(avg_loss))

    # Log the running loss averaged per batch
    # for both training and validation
    writer.add_scalars('Training vs. Validation Loss',
                    { 'Training' : avg_loss},
                    epoch_number + 1)
    writer.flush()

    # Track best performance, and save the model's state
    if avg_loss < best_vloss:
        best_vloss = avg_loss
        model_path = 'model_{}_{}'.format(timestamp, epoch_number)
        torch.save(model.state_dict(), model_path)

    epoch_number += 1