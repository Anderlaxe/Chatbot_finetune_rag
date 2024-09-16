"""
Main module used to finetune Mistral.
"""

###############
### Imports ###
###############

### Python imports ###

from accelerate import (
    FullyShardedDataParallelPlugin,
    Accelerator
)
import torch
from torch.distributed.fsdp.fully_sharded_data_parallel import (
    FullOptimStateDictConfig,
    FullStateDictConfig
)
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)
from peft import (
    prepare_model_for_kbit_training,
    LoraConfig,
    get_peft_model
)
import transformers
from datetime import datetime

### Module imports ###

from tools.tools_constants import (
    PATH_TRAIN_SET_CHAT,
    PATH_TEST_TRAIN_SET,
    BASE_MODEL_ID,
    TEST_MODEL_BEFORE_TRAINING,
    MODE_CHAT,
    PATH_SAVE_MODEL_CHAT,
    NUMBER_EPOCHS
)

from tools.tools_dataset import (
    load_database,
    provide_test_base
)

from tools.tools_models import (
    tokenizer,
    generate_and_tokenize_prompt_chatbot,
    bnb_config
)

#################
### Main code ###
#################

print("----------- Initialization -----------")

fsdp_plugin = FullyShardedDataParallelPlugin(
    state_dict_config=FullStateDictConfig(
        offload_to_cpu=True, rank0_only=False),
    optim_state_dict_config=FullOptimStateDictConfig(
        offload_to_cpu=True, rank0_only=False),
)

accelerator = Accelerator(fsdp_plugin=fsdp_plugin)

print("----------- Load dataset -----------")

train_dataset = load_database(path_database=PATH_TRAIN_SET_CHAT)
eval_dataset = load_database(path_database=PATH_TEST_TRAIN_SET)

print("----------- Load Base Model -----------")

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID,
    quantization_config=bnb_config
)

print("----------- Tokenization -----------")

tokenizer.pad_token = tokenizer.eos_token

tokenized_train_dataset = train_dataset.map(generate_and_tokenize_prompt_chatbot)
tokenized_val_dataset = eval_dataset.map(generate_and_tokenize_prompt_chatbot)

if TEST_MODEL_BEFORE_TRAINING:
    test_questions = provide_test_base()

    # Re-init the tokenizer so it doesn't add padding or eos token
    eval_tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL_ID,
        add_bos_token=True,
    )

    model_input = eval_tokenizer(test_questions, return_tensors="pt").to("cuda")

    model.eval()
    with torch.no_grad():
        print(eval_tokenizer.decode(
            model.generate(**model_input, max_new_tokens=256)[0],
            skip_special_tokens=True))

print("----------- Set up Lora -----------")

model.gradient_checkpointing_enable()
model = prepare_model_for_kbit_training(model)

config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
        "lm_head"
    ],
    bias="none",
    lora_dropout=0.05,  # Conventional
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, config)

# Apply the accelerator. You can comment this out to remove the accelerator.
model = accelerator.prepare_model(model)

print("----------- Training -----------")

if torch.cuda.device_count() > 1: # If more than 1 GPU
    model.is_parallelizable = True
    model.model_parallel = True

tokenizer.pad_token = tokenizer.eos_token

trainer = transformers.Trainer(
    model=model,
    train_dataset=tokenized_train_dataset,
    eval_dataset=tokenized_val_dataset,
    args=transformers.TrainingArguments(
        output_dir=PATH_SAVE_MODEL_CHAT,
        warmup_steps=5,
        per_device_train_batch_size=2,
        gradient_checkpointing=True,
        gradient_accumulation_steps=4,
        max_steps=NUMBER_EPOCHS,
        learning_rate=2.5e-5, # Want about 10x smaller than the Mistral learning rate
        logging_steps=50,
        bf16=True,
        optim="paged_adamw_8bit",
        logging_dir="./logs",  # Directory for storing logs
        save_strategy="steps", # Save the model checkpoint every logging step
        save_steps=50, # Save checkpoints every 50 steps
        evaluation_strategy="steps", # Evaluate the model every logging step
        eval_steps=50,  # Evaluate checkpoints every 50 steps
        do_eval=True,   # Perform evaluation at the end of training
        report_to="none",
        run_name=f"{MODE_CHAT}-{datetime.now().strftime('%Y-%m-%d-%H-%M')}"          # Name of the W&B run (optional)
    ),
    data_collator=transformers.DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

# Silence the warnings
model.config.use_cache = False
trainer.train()
