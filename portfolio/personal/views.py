# Create your views here.
import json
import logging
import os
import re
from functools import lru_cache

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from directRetrieval.qna import QnAModel

from .llm import OpenRouterLLM, approved_answer
from .models import Project
from .orouter import OpenRouterError

log = logging.getLogger(__name__)

# load file at static/cris.config
crisConfigPath = os.path.join(settings.STATIC_ROOT, "cris.config")
print(f"Loading cris config from {crisConfigPath}")
config = json.load(open(crisConfigPath, 'r'))
config['qna'] = os.path.join(settings.STATIC_ROOT, config['qna'])

# The demo asks a free OpenRouter model, picked at runtime (see llm.py).
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
qnaModel = None
if OPENROUTER_API_KEY:
    llm = OpenRouterLLM(OPENROUTER_API_KEY)
    qnaModel = QnAModel.fromConfig(llm, config)
    llm.selector.warm_up()
else:
    print("OPENROUTER_API_KEY is not set: the question answering demo is disabled")


@lru_cache(maxsize=512)
def cached_answer(normalized_question: str) -> str:
    # Exceptions are not cached, so a failed call is retried on the next ask.
    return approved_answer(qnaModel, normalized_question)


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
        question = request.POST.get('question', '').strip()
        if not question:
            return JsonResponse({"error": "Please type a question."}, status=400)
        if qnaModel is None:
            return JsonResponse({"error": "The demo is not configured right now."}, status=503)
        normalized = re.sub(r"\s+", " ", question)[:500]
        try:
            answer = cached_answer(normalized)
        except Exception:
            log.exception("question answering failed")
            return JsonResponse(
                {"error": "The AI provider is busy right now. Please try again in a minute."},
                status=503,
            )
        return JsonResponse({"last_question": question, "last_answer": answer})
    return render(request, 'personal/answer-demo.html', {"last_question": "", "last_answer": ""})
