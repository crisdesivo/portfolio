"""Question answering through a free OpenRouter model chosen at runtime.

No model is hard-coded: free models come and go, so the model is picked with
`best_structured_model()` from orouter (copied unchanged from the separate
~/Proyectos/openrouter project into personal/orouter.py). That walks the free
models ranked by size x usage and returns the first one that demonstrably
honours a JSON schema. The choice is redone when it gets old or starts failing.

The answer itself is still validated server-side in `approved_answer()`, so a
model that ignores the schema can only cause "no answer", never an unapproved one.
"""
import fcntl
import json
import logging
import os
import threading
import time
from typing import Dict, List, Optional, Union

from directRetrieval.LLMInterfaces import SyncLLMInterface
from directRetrieval.qna import QnAModel

from . import orouter

log = logging.getLogger(__name__)

RESELECT_AFTER = 6 * 3600  # seconds a chosen model is trusted before re-checking
REQUEST_TIMEOUT = 60.0     # free models queue; keep under gunicorn's 120 s timeout
MAX_ATTEMPTS = 3

# Gunicorn workers share the container's /tmp, so one worker's selection serves
# all of them and the selection test (several model requests) runs only once.
CACHE_PATH = "/tmp/orouter_selected_model.json"
LOCK_PATH = CACHE_PATH + ".lock"


class ModelSelector:
    """Keeps the currently selected free model, shared across worker processes."""

    def __init__(self, client: orouter.Client):
        self.client = client
        self._thread_lock = threading.Lock()

    def _read(self) -> Optional[Dict]:
        try:
            with open(CACHE_PATH, encoding="utf-8") as f:
                cached = json.load(f)
        except (OSError, ValueError):
            return None
        if time.time() - cached.get("chosen_at", 0) > RESELECT_AFTER:
            return None
        return cached

    def get(self) -> str:
        cached = self._read()
        if cached:
            return cached["model"]
        with self._thread_lock, open(LOCK_PATH, "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)  # another worker may be selecting
            cached = self._read()
            if cached:
                return cached["model"]
            winner, verdicts = orouter.best_structured_model(client=self.client)
            for verdict in verdicts:
                log.info("orouter candidate %s: %s", verdict.model_id, verdict.reason)
            if winner is None:
                raise orouter.OpenRouterError("no free model currently honours a JSON schema")
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump({"model": winner.id, "chosen_at": time.time()}, f)
            log.info("orouter selected %s", winner.id)
            return winner.id

    def invalidate(self, model: str) -> None:
        """Forget `model` so the next request selects again."""
        cached = self._read()
        if cached and cached["model"] == model:
            try:
                os.remove(CACHE_PATH)
            except OSError:
                pass

    def warm_up(self) -> None:
        """Select in the background so the first visitor doesn't wait for it."""
        def run():
            try:
                self.get()
            except Exception:
                log.exception("orouter warm-up selection failed")
        threading.Thread(target=run, daemon=True).start()


class OpenRouterLLM(SyncLLMInterface):
    """directRetrieval interface backed by the selected free OpenRouter model."""

    def __init__(self, api_key: str):
        self.client = orouter.Client(api_key=api_key, timeout=REQUEST_TIMEOUT)
        self.selector = ModelSelector(self.client)

    def getResponse(
        self,
        messages: List[Dict[str, str]],
        properties: Union[Dict, None],
        temperature: int = 0,
        stream: bool = False,
    ) -> Union[Dict, str]:
        assert not stream, "streaming is not used by the demo"
        params: Dict = {"temperature": temperature, "max_tokens": 2000}
        if properties is not None:
            params["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": "QnA",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": properties,
                        "required": list(properties.keys()),
                        "additionalProperties": False,
                    },
                },
            }

        model = self.selector.get()
        for attempt in range(MAX_ATTEMPTS):
            last = attempt == MAX_ATTEMPTS - 1
            try:
                data = self.client.complete(messages, model=model, **params)
            except orouter.OpenRouterError as exc:
                if orouter._is_transient(str(exc)) and not last:
                    time.sleep(2 * (attempt + 1))
                    continue
                # Not a hiccup: drop this model so the next request re-selects.
                self.selector.invalidate(model)
                raise
            content = data["choices"][0]["message"].get("content") or ""
            if properties is None:
                return content
            try:
                return json.loads(content)
            except ValueError:
                if not last:
                    continue
                self.selector.invalidate(model)
                raise orouter.OpenRouterError(f"{model} returned non-JSON output")
        raise orouter.OpenRouterError("no response after retries")


def approved_answer(qna_model: QnAModel, question: str) -> str:
    """The pre-written answer the model selected, or "" if none fits.

    Everything the model returns is checked against the QnA list here, so what is
    shown is always one of the approved answers, verbatim, whatever the model does.
    """
    response = qna_model.getJSONAnswer(question)
    if not isinstance(response, dict) or response.get("Is_answer_in_QnA") is not True:
        return ""
    chosen = response.get(QnAModel.ANSWER_KEY)
    if not isinstance(chosen, dict):
        return ""
    number = chosen.get("question_number")
    if not isinstance(number, int) or not 0 <= number < len(qna_model.qna):
        return ""
    item = qna_model.qna[number]
    if chosen.get("question") != item.question:
        return ""  # the number and the question disagree: don't guess which one
    return item.answer
