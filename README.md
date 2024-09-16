# Benchmark of open-source LLM and creation of a chatbot answering questions

## Table of contents

- [Benchmark of open-source LLM and creation of a chatbot answering questions about university curriculum](#benchmark-of-open-source-llm-and-creation-of-a-chatbot-answering-questions-about-university-curriculum)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Project architecture](#project-architecture)
  - [Benchmark of open-source generative AI](#benchmark-of-open-source-generative-ai)
    - [Mistral](#mistral)
    - [GPT models](#gpt-models)
  - [Creation of the chatbot](#creation-of-the-chatbot)
    - [First web interface for the chatbot](#first-web-interface-for-the-chatbot)

## Introduction

The goal of the project is to realize a benchmark of the most performing open-source LLM, such as Mistral, Llama 2, Falcon, CroissantLLM and Mixtral.

It has for application the creation of a chatbot answering questions about the curriculum of a university.

This project has been realized by:
- Clément CHARDINE
- Alexandre PETIT
- Agathe PLU

## Project architecture

This repository is composed of the following folders:
- `azure`, containing the whole pipeline for the reference chatbot running with OpenAI models. It also contains the *Python* scripts to launch the evaluation with the GPT-Judge called `testEvaluation.py`, `testEvaluationMixtral.py`, `testEvaluationMistral.py` and `test_evaluation_mistral.py`. The three first ones launch the corresponding model with the evaluation on the whole test database, whereas the last one uses directly the results already inferred by Mistral. It also contains the script `viz.py` and `viz_mistral.py` to create the visualisation graphs with the results of similarity and uncertainty created by the GPT-Judge, by using the *csv* files saved in the folder `results_gpt_judge`.
- `batch`, containing the *sbatch* files launching the finetuning or the executions of the open-source LLM on the clusters. Some batchs are only for the DCE, or for the DCE, according to their names, because the configurations are different on both clusters. It also contains the *sbatch* file to create the virtual environment on the cluster with all requirements, called `slurm-conda-setup.sbatch`.
- `chatbot`, containing the React first interface of the chatbot.
- `database`, containing:
  - the Python script `convert_form_json.py`, converting the results of the form (the list of students' questions gathered in the study in `form_results.csv`) into the json file `test_base.json`.
  - the Python script `filter_database.py`, which loads the json file `database.json` of the folder `scrapping` and post-processes it by removing fields with only titles or redundant ones, and by cleaning them by removing the special characters *==* or *--* which can be found in Markdown after the scrapping. It then creates the clean files `database.json` and `database_rde.json` in the current folder. The `database_rde.json` contains only the information coming of the extraction of the RDE, which has been detected more reliable than the whole database.
  - the files `train_base.json` and `notes.json`, corresponding to the train base for the finetuning of the LLM. The first file contains a list of questions and answers, whereas the second one contains the raw database.
  - the databases in French and in English for the tests on the Mistral
- `embeddings`, containing the embedded database created by *Langchain* for the embeddings for the execution of Mistral.
- `models`, containing the models of Mistral, after their finetuning.
- `results`, containing the results of the several executions of Mistral, may it be with or without finetuning or embeddings, on the university's database.
- `scrapping`, containing the scrapping script `scraper.py`, which permits us to gather the information present on the university's websites.
- `tools`, containing several tools for the execution and finetuning of the different models. It contains the files:
  - `tools_basis.py`, with some basic tools functions.
  - `tools_constants.py`, with the main constants of the code (and thus configuration of the training and execution)
  - `tools_dataset.py`, with the function to load and create the dataset for finetuning and embeddings.
  - `tools_models.py`, with the loading of models
  - `tools_rag.py`, with the tools functions to create the RAG architecture and the embedding database.
  - `tools_results.py`, with the functions post-processing the results obtained with Mistral.

This repository contains the following files:
- `analyse_results.py`, a *Python* script analyzing the results provided by the GPT-Judge and stored in the *csv* files in `azure/results_gpt_judge/`.
- `clear_chatbot_output.py`, a *Python* script used to clear the output of Mistral contained in `results`, before passing it into the GPT-judge.
- `croissant-rag.py`, *Python* file to execute the model Croissant LLM with the RAG
- `mistral-execution-chat-no-finetuning.py` to launch Mistral without finetuning or RAG.
- `mistral-execution-chat-text.py`, `mistral-execution-chat.py` and `mistral-execution-text.py` to launch the finetuned model of Mistral, may the finetune is done in chat, chat-text or text mode.
- `mistral-finetune-chat-text.py`, `mistral-finetune-chat.py` and `mistral-finetune-text.py` to launch the finetuning of the model selected in `tools_constants.py`.
- `mixtral_inference.py`, `mixtral_rag.py` and `mixtral_train.py` to launch Mitral, with or without RAG or finetuning.

## Benchmark of open-source generative AI

We have tested several open-source models in our project and also GPT with or without finetuning or RAG architecture.

### Mistral

The benchmark pipeline with the Mistral models can be parametrized with the file `tools_constants.py`. First of all, the user needs to choose a model deriving from Mistral available on HuggingFace: 4 are already listed in `LIST_BASE_MODEL_ID` and the user may add some. The user then has to change the index in `BASE_MODEL_ID` to select the desired modele. It can then name the training session by changing `GLOBAL_MODE`. If the user wants to finetune the model, may it be in chat, text or chat-text mode, it can change the number of epochs. Finally, if the user wants to use embeddings, it has to determine if it is the first time it is using this model. If it is, it must set the constant `FIRST_TIME_EMBEDDINGS` to True, otherwise to False.

If the user wants to run the finetuning, embeddings or execution scripts on the DCE it has to use the following commands.

First of all, it needs to create its virtual environment by running the command:
```bash
sbatch batch/slurm-conda-setup.sbatch
```

It can test if the virtual environment is working by running the batch:
```bash
sbatch batch/test-conda-setup.sbatch
```

To launch the finetuning of the desired model of Mistral, the user has to run the following commands, depending on the mode:
```bash
sbatch batch/launch-mistral-finetuning-text.sbatch
sbatch batch/launch-mistral-finetuning-chat.sbatch
sbatch batch/launch-mistral-finetuning-chat-text.sbatch
```

To launch the execution of the formerly finetuned model of Mistral, the user has to run the following commands, depending on the mode:
```bash
sbatch batch/launch-mistral-execution-text.sbatch
sbatch batch/launch-mistral-execution-chat.sbatch
sbatch batch/launch-mistral-execution-chat-text.sbatch
```

To launch the execution of the desired model of Mistral without any finetuning nor embeddings, the user has to run the following command:
```bash
sbatch batch/launch-mistral-execution-chat-no-finetuning.sbatch
```

To launch the execution of the desired model of Mistral with only the embeddings, the user has to run the following commands, depending on the database he wants to use:
```bash
sbatch batch/launch-embeddings.sbatch
```

### GPT models

The benchmark pipeline with the GPT4 model, with embeddings created with GPT4, can be launched with the following command:

```bash
python testEvaluation.py
```

## Creation of the chatbot

### First web interface for the chatbot

In order to launch the first web interface with the small widget, go to the folder `chatbot` with the following command:

```bash
cd chatbot
```

For the first time, install all packages of the chatbot with the following command:

```bash
npm i
```

Then, launch the web interface with the following command:
```bash
npm run dev
```

The web interface can thus be found under the following url:
```bash
http://localhost:5173/
```
