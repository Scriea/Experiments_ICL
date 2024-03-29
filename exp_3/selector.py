import random
from rank_bm25 import BM25Okapi
import json
import numpy as np
from bert_score import score


def get_demonstrations_random_wiki(include_answers=True, have_context=False)-> str:
    path = "../data/icl_wiki_examples.json"
    prompt = ""
    with open(path) as f:
        demonstrations = json.load(f)

    for demo in demonstrations:
        question = demo["question"]
        answer = demo["answer"]
        context = demo["contents"]
        if include_answers:
            if have_context:
                prompt+= f"\n Context:{context}\nQuestion: {question}?\nAnswer: {answer}\n"
            else:
                prompt+= f"\nQuestion: {question} ? \nOutput:{{\n Context: {context}\n Answer: {answer} }}\n"

        else:
            prompt+= f"\nQuestion: {question} ?\nContext: {context}\n"

    return prompt

def get_demonstrations_random(icl_dataset:list, k:int=3)-> str:
    prompt = ""
    demonstrations = random.sample([i for i in range(len(icl_dataset))], k)
    for i in demonstrations:
        demo = icl_dataset[i]
        question = demo["question"]
        answer = "".join(demo["answer"])
        context = demo["context"]
        prompt+= f"\nQuestion: {question} \nOutput:{{ Context: {context} Answer: {answer} }}\n"
    return prompt + "<EOE>\n"

# def get_demonstrations_coverage(icl_dataset:list, k:int=3)-> str:
#     prompt = ""
#     demonstrations = random.sample([i for i in range(len(icl_dataset))], k)
#     for i in demonstrations:
#         demo = icl_dataset[i]
#         question = demo["question"]
#         answer = demo["anwer"]
#         context = demo["context"]
#         prompt+= f"Question: {question}\nContext: {context}\nAnswer: {answer}\n"
#     return prompt + "<EOE>\n"

def get_demonstrations_bm25(icl_dataset:list, corpus, bm25, query:str, k:int=3)-> str:
    prompt = ""
    tokenized_query = query.split(" ")
    doc_scores = bm25.get_scores(tokenized_query)
    demonstrations=np.argsort(-doc_scores)[:k]
    for i in demonstrations:
        demo = icl_dataset[i]
        question = demo["question"]
        answer = " ".join(demo["answer"])
        context = demo["context"]
        prompt+= f"Question: {question} \nOutput:{{Context: {context} Answer: {answer}}}\n"
    return prompt + "<EOE>\n"

def get_demonstrations_bert(query:str, documents, icl_dataset, k:int=3)-> str:
    BSR = []
    for doc in documents:
        P, R, F1 = score([doc], [query], lang="en", verbose=False, model_type="bert-base-uncased", use_fast_tokenizer=True)
        BSR.append(R.item())
    BSR = np.array(BSR)

    demonstrations = np.argpartition(BSR, -k)[-k:]
    prompt = ""
    for i in demonstrations:
        demo = icl_dataset[i]
        question = demo["question"]
        answer = "".join(demo["answer"])
        context = demo["context"]
        prompt+= f"Question: {question}\nOutput:{{Context: {context} Answer: {answer}}}\n"
    return prompt + "<EOE>"

