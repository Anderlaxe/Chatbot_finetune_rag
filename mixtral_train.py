import torch
import transformers
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model, PeftModel


tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-Instruct-v0.1")
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    load_in_4bit=True,
    torch_dtype=torch.float16,
    device_map="auto",
    )

model = prepare_model_for_kbit_training(model)

print("Model loaded")

tokenizer.pad_token = "!"

CUTOFF_LEN = 256  #Our dataset has short text
LORA_R = 8
LORA_ALPHA = 2 * LORA_R
LORA_DROPOUT = 0.1

config = LoraConfig(
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    target_modules=[ "w1", "w2", "w3"],  #just targetting the MoE layers.
    lora_dropout=LORA_DROPOUT,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, config)
model.print_trainable_parameters()

dataset = load_dataset("database/train_base.json")
print("dataset", dataset)
train_data = dataset["train"] # Not using evaluation data

def generate_prompt(user_query):
    sys_msg= "Tu es le chatbot de l'université. Réponds en Français à la requête de l'utilisateur, en utilisant les données sur l'université que tu as apprises. Si tu ne sais pas comment répondre, admets-le mais ne répond pas quelque chose de faux. Réponds dans un Français correct et bien formulé. Ne cite pas mot pour mot les données de l'université, reformule ta réponse. La réponse doit ête concise et précise. Si la question posée ne concerne pas l'université ni des sujets qui en sont proches, répond que la question est hors contexte"
    p =  "<s> [INST]" + sys_msg +"\n"+ user_query["question"] + "[/INST]" +  user_query["answer"] + "</s>"
    return p 

def tokenize(prompt):
    return tokenizer(
        prompt + tokenizer.eos_token,
        truncation=True,
        max_length=CUTOFF_LEN ,
        padding="max_length"
    )

train_data = train_data.shuffle().map(lambda x: tokenize(generate_prompt(x)), remove_columns=["answer" , "question"])

trainer = Trainer(
    model=model,
    train_dataset=train_data,
    args=TrainingArguments(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        num_train_epochs=6,
        learning_rate=1e-4,
        logging_steps=2,
        optim="adamw_torch",
        save_strategy="epoch",
        output_dir="mixtral-lora-instruct-cs"
    ),
    data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False)
)
model.config.use_cache = False

print("Start training")

trainer.train()