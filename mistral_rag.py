"""
Main module to execute Mistral without finetuning and with RAG.
"""

###############
### Imports ###
###############

### Python imports ###

import os
import torch
import time
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from transformers import AutoModelForCausalLM, pipeline, BitsAndBytesConfig

### Local imports ###

from tools.tools_basis import (
    save_txt_file,
    load_json_file
)
from tools.tools_constants import (
    BASE_MODEL_ID,
    DELIMITATION_CHARACTER,
    LANGUAGE,
    GLOBAL_MODE,
    FIRST_TIME_EMBEDDINGS,
    PATH_TEST_SET
)
from tools.tools_models import (
    tokenizer
)
from tools.tools_rag import (
    create_db,
    load_retriever,
    create_chain_prompt,
    ask_question_embeddings
)

#################
### Main code ###
#################

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16
    )

model_kwargs = {'device': 'cuda'}

embeddings = HuggingFaceEmbeddings(
    model_kwargs=model_kwargs)

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_ID, device_map='auto', quantization_config=quantization_config)


pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=300)
llm = HuggingFacePipeline(pipeline=pipe)

if FIRST_TIME_EMBEDDINGS:
    create_db(embeddings=embeddings)

zero_time = time.time()
# Load the retriever
retriever = load_retriever(embeddings=embeddings)

# Create the chain with the prompt
chain = create_chain_prompt(llm=llm)

# Answer to these questions

test_base = load_json_file(file_path=PATH_TEST_SET)["dataset"]
list_questions = []
for question in test_base:
    list_questions.append(question["question"])

output = ""

start_time = time.time()
for question in list_questions:
    output += "QUESTION " + question
    output += "\nANSWER" + ask_question_embeddings(
        retriever=retriever,
        chain=chain,
        question=question)
    output += DELIMITATION_CHARACTER
end_time = time.time()
print("Computation time : ", end_time-start_time)
print("Whole time : ", end_time-zero_time)

output_dir = "results/cs_full_embeddings/"
# Create the directory if needed
try:
    os.mkdir(output_dir)
except:
    pass

# Save the results
save_txt_file(
    file_path=output_dir + GLOBAL_MODE + "_" + LANGUAGE + ".txt",
    content=output)
