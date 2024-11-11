# Create your views here.
from django.shortcuts import render
from .models import Project
import json
import os
from django.conf import settings
from llama_cpp import Llama
from django.http import JsonResponse
import sys
from threading import Lock
from directRetrieval.qna import QnAModel
from directRetrieval.LLMInterfaces import LLamaCPP

# TODO use openai?
# TODO upload to cloud run as is to test
# TODO then download from the script https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q5_k_m.gguf
# TODO use llama_cpp python module to load the model
# TODO add a view to interact with the model, a chat
# Google Cloud Run supposedly has 8 GB of storage which should be enough for the 1.3 GB model

llmLock = Lock()
ggufPath = os.path.join(settings.STATIC_ROOT, "qwen2.5-1.5b-instruct-q5_k_m.gguf")
try:
    llm = LLamaCPP(ggufPath, n_ctx=2500)
except Exception as e:
    print(f"Failed to load model from {ggufPath}")
    print(e)
    # sys.exit(1)

# load file at static/cris.config
crisConfigPath = os.path.join(settings.STATIC_ROOT, "cris.config")
print(f"Loading cris config from {crisConfigPath}")
config = json.load(open(crisConfigPath, 'r'))
config['qna'] = os.path.join(settings.STATIC_ROOT, config['qna'])
qnaModel = QnAModel.fromConfig(llm, config)


# make views for individual projects
def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    return render(request, 'personal/project_detail.html', {'project': project})

# show all projects
def home(request):
    projects = Project.objects.all()
    # sort projects by priority (highest first)
    projects = sorted(projects, key=lambda x: x.priority, reverse=True)
    return render(request, 'personal/home.html', {'projects': projects})

# hire me page
def hire_me(request):
    return render(request, 'personal/hire_me.html', {})

def ask_question(request):
    if request.method == 'POST':
        data = request.POST
        print(data)
        question = data['question']
        print(question)
        with llmLock:
            answer = qnaModel.getAnswer(question)
        # return render(request, 'personal/answer-demo.html', {"last_question": question, "last_answer": answer})
        return JsonResponse({"last_question": question, "last_answer": answer})
    return render(request, 'personal/answer-demo.html', {"last_question": "", "last_answer": ""})
