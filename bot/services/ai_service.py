"""
Searcharr AI chat service with model router (OpenAI-compatible aggregators).
"""
import asyncio
import itertools
import json
import os
import re
import tempfile
from threading import Lock

from openai import AsyncOpenAI

from bot.utils.database import DBPATH
from bot.utils.log import set_up_logger
import settings

logger = set_up_logger("services.ai")

DEFAULT_SYSTEM_PROMPT = (
    "Ты дружелюбный ассистент HarborTV / Searcharr в Telegram. "
    "Помогаешь с фильмами и сериалами, советами что посмотреть. "
    "Если пользователь хочет добавить тайтл в библиотеку, подскажи команды "
    "/movie и /series. Отвечай кратко и по делу. "
    "В группах учитывай текущий режим: отвечать всем или только по обращению; "
    "а также разрешено ли общение в личных сообщениях."
)

CATEGORIES = ("light", "general", "complex")
DEFAULT_CONTEXT_FILE = "ai_contexts.json"

# Defaults aligned with OpenRouter free-tier catalog (override in settings.py)
DEFAULT_ROUTER_MODEL = "nvidia/nemotron-3.5-lightning:free"
DEFAULT_MODELS_LIGHT = ["nvidia/nemotron-3-super:free"]
DEFAULT_MODELS_GENERAL = ["google/gemma-4-31b:free"]
DEFAULT_MODELS_COMPLEX = ["dots-studio/dots-3-note-preview:free"]

ROUTER_PROMPT = """Проанализируй запрос пользователя и выбери для него наиболее подходящий тип модели.
Ответь СТРОГО ОДНИМ СЛОВОМ из трёх вариантов: light, general или complex. Никакого другого текста.

Критерии выбора:
- complex: сложные задачи на логику, математику, написание кода, глубокий анализ, нестандартные головоломки.
- light: простые приветствия ('привет', 'как дела'), светская беседа (small talk), базовые вопросы, шутки.
- general: все остальные стандартные запросы (статьи, перевод, рецепты, фильмы/сериалы, история/география).

Запрос пользователя: "{user_text}"
Твой вердикт:"""


def _normalize_base_url(url: str) -> str:
    """Ensure OpenAI client base_url includes the /v1 API suffix."""
    base = (url or "").strip().rstrip("/")
    if not base:
        return base
    if base.endswith("/v1"):
        return base
    if "openrouter.ai" in base.lower():
        if base.endswith("/api"):
            return f"{base}/v1"
        return f"{base}/api/v1"
    if base.endswith("/api"):
        return f"{base}/v1"
    return f"{base}/v1"


def _as_model_list(value) -> list:
    """Normalize setting value to a non-empty stripped model id list."""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    result = []
    for item in value:
        model = str(item).strip()
        if model:
            result.append(model)
    return result


class AiChatService:
    """In-memory AI client with dispatcher, model pools, and disk persistence."""

    def __init__(self):
        self.enabled = bool(getattr(settings, "ai_enabled", False))
        self.api_key = (getattr(settings, "ai_api_key", "") or "").strip()
        self.base_url = _normalize_base_url(
            getattr(settings, "ai_base_url", "") or ""
        )
        self.system_prompt = (
            getattr(settings, "ai_system_prompt", "") or DEFAULT_SYSTEM_PROMPT
        ).strip()
        self.max_context = int(getattr(settings, "ai_max_context", 10) or 10)
        self.router_enabled = bool(getattr(settings, "ai_router_enabled", True))
        self.router_model = (
            getattr(settings, "ai_router_model", "") or DEFAULT_ROUTER_MODEL
        ).strip()
        try:
            self.router_timeout = float(
                getattr(settings, "ai_router_timeout", 5.0) or 5.0
            )
        except (TypeError, ValueError):
            self.router_timeout = 5.0
        if self.router_timeout < 1.0:
            self.router_timeout = 1.0
        self.announce_route = bool(getattr(settings, "ai_announce_route", False))

        self.persist_enabled = bool(
            getattr(settings, "ai_context_persist", True)
        )
        self.save_interval = int(
            getattr(settings, "ai_context_save_interval", 60) or 60
        )
        if self.save_interval < 5:
            self.save_interval = 5

        custom_path = (getattr(settings, "ai_context_file", "") or "").strip()
        if custom_path:
            self.context_path = (
                custom_path
                if os.path.isabs(custom_path)
                else os.path.join(DBPATH, custom_path)
            )
        else:
            self.context_path = os.path.join(DBPATH, DEFAULT_CONTEXT_FILE)

        legacy = (getattr(settings, "ai_model", "") or "").strip()
        self.models = {
            "light": _as_model_list(getattr(settings, "ai_models_light", None)),
            "general": _as_model_list(
                getattr(settings, "ai_models_general", None)
            ),
            "complex": _as_model_list(
                getattr(settings, "ai_models_complex", None)
            ),
        }
        if legacy and not self.models["general"]:
            self.models["general"] = [legacy]

        self._rr = {
            cat: itertools.cycle(models) if models else None
            for cat, models in self.models.items()
        }
        self._contexts = {}
        self._contexts_lock = Lock()
        self._dirty = False
        self._client = None
        self._persist_task = None

        if not self.enabled:
            logger.info("AI chat is disabled in settings")
            return

        has_any_model = any(self.models.values())
        if not self.api_key or not self.base_url or not has_any_model:
            logger.warning(
                "AI chat enabled but ai_api_key / ai_base_url / model pools "
                "are incomplete — AI features will stay off."
            )
            self.enabled = False
            return

        if self.router_enabled and not self.router_model:
            logger.warning(
                "ai_router_enabled=True but ai_router_model is empty; "
                "falling back to general pool without routing."
            )
            self.router_enabled = False

        client_kwargs = {
            "api_key": self.api_key,
            "base_url": self.base_url,
        }
        # OpenRouter recommends identifying the app for free-tier routing/stats
        if "openrouter.ai" in self.base_url.lower():
            client_kwargs["default_headers"] = {
                "HTTP-Referer": "https://github.com/ha-harbor-ws/searcharr",
                "X-Title": "HarborTVbot",
            }
        self._client = AsyncOpenAI(**client_kwargs)
        self.load_contexts()
        logger.info(
            "AI chat ready: base_url=%s router=%s (%s, timeout=%ss) "
            "max_context=%s persist=%s interval=%ss file=%s pools=%s",
            self.base_url,
            self.router_enabled,
            self.router_model or "-",
            self.router_timeout,
            self.max_context,
            self.persist_enabled,
            self.save_interval,
            self.context_path,
            {k: v for k, v in self.models.items()},
        )

    def _mark_dirty(self):
        self._dirty = True

    def clear_context(self, context_key: str):
        """Reset conversation history for a context key."""
        with self._contexts_lock:
            self._contexts[context_key] = [
                {"role": "system", "content": self.system_prompt}
            ]
            self._mark_dirty()

    def _ensure_context(self, context_key: str):
        if context_key not in self._contexts or not self._contexts[context_key]:
            self.clear_context(context_key)

    def _trim_context(self, context_key: str):
        history = self._contexts[context_key]
        if len(history) <= self.max_context:
            return
        system = history[0]
        tail = history[-(self.max_context - 1) :]
        self._contexts[context_key] = [system] + tail

    def load_contexts(self):
        """Load persisted contexts from disk into memory."""
        if not self.persist_enabled:
            return
        if not os.path.isfile(self.context_path):
            logger.debug("No AI context file at %s", self.context_path)
            return
        try:
            with open(self.context_path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            contexts = payload.get("contexts", payload)
            if not isinstance(contexts, dict):
                logger.warning("Invalid AI context file format, ignoring")
                return

            loaded = 0
            with self._contexts_lock:
                for key, messages in contexts.items():
                    if not isinstance(key, str) or not isinstance(messages, list):
                        continue
                    cleaned = []
                    for msg in messages:
                        if (
                            isinstance(msg, dict)
                            and msg.get("role") in ("system", "user", "assistant")
                            and isinstance(msg.get("content"), str)
                        ):
                            cleaned.append(
                                {"role": msg["role"], "content": msg["content"]}
                            )
                    if not cleaned:
                        continue
                    if cleaned[0]["role"] == "system":
                        cleaned[0]["content"] = self.system_prompt
                    else:
                        cleaned.insert(
                            0, {"role": "system", "content": self.system_prompt}
                        )
                    self._contexts[key] = cleaned
                    self._trim_context(key)
                    loaded += 1
                self._dirty = False
            logger.info(
                "Loaded %s AI context(s) from %s", loaded, self.context_path
            )
        except Exception as e:
            logger.error("Failed to load AI contexts: %s", e)

    def save_contexts(self, force=False):
        """Persist in-memory contexts to disk (atomic replace)."""
        if not self.persist_enabled:
            return
        if not force and not self._dirty:
            return

        try:
            os.makedirs(os.path.dirname(self.context_path) or ".", exist_ok=True)
            with self._contexts_lock:
                snapshot = {
                    "version": 1,
                    "contexts": {
                        key: list(messages)
                        for key, messages in self._contexts.items()
                        if messages
                    },
                }
            directory = os.path.dirname(self.context_path) or "."
            fd, tmp_path = tempfile.mkstemp(
                prefix="ai_contexts_", suffix=".json", dir=directory
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    json.dump(snapshot, fh, ensure_ascii=False, indent=2)
                os.replace(tmp_path, self.context_path)
            except Exception:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
                raise

            self._dirty = False
            logger.debug(
                "Saved %s AI context(s) to %s",
                len(snapshot["contexts"]),
                self.context_path,
            )
        except Exception as e:
            logger.error("Failed to save AI contexts: %s", e)

    async def start_persistence(self):
        """Start periodic disk flush background task."""
        if not self.enabled or not self.persist_enabled:
            return
        if self._persist_task and not self._persist_task.done():
            return

        async def _loop():
            logger.info(
                "AI context autosave every %s seconds → %s",
                self.save_interval,
                self.context_path,
            )
            try:
                while True:
                    await asyncio.sleep(self.save_interval)
                    await asyncio.to_thread(self.save_contexts)
            except asyncio.CancelledError:
                await asyncio.to_thread(self.save_contexts, True)
                raise

        self._persist_task = asyncio.create_task(_loop())

    async def stop_persistence(self):
        """Stop autosave task and flush once."""
        if self._persist_task:
            self._persist_task.cancel()
            try:
                await self._persist_task
            except asyncio.CancelledError:
                pass
            self._persist_task = None
        await asyncio.to_thread(self.save_contexts, True)

    def _pick_models(self, category: str) -> list:
        """Ordered candidate models for a category (RR start + rest as fallback)."""
        if category not in CATEGORIES:
            category = "general"
        pool = self.models.get(category) or []
        if not pool:
            for fallback in ("general", "light", "complex"):
                if self.models.get(fallback):
                    pool = self.models[fallback]
                    category = fallback
                    break
        if not pool:
            return []

        if self._rr.get(category) is None:
            self._rr[category] = itertools.cycle(pool)
        start = next(self._rr[category])
        ordered = [start]
        for model in pool:
            if model != start:
                ordered.append(model)
        seen = set()
        unique = []
        for model in ordered:
            if model not in seen:
                seen.add(model)
                unique.append(model)
        return unique

    async def route_request(self, user_text: str) -> str:
        """Dispatcher: return light / general / complex."""
        if not self.router_enabled or not self.router_model:
            return "general"

        prompt = ROUTER_PROMPT.format(user_text=user_text.replace('"', "'"))
        try:
            response = await self._client.chat.completions.create(
                model=self.router_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=5,
                timeout=self.router_timeout,
            )
            raw = (response.choices[0].message.content or "").strip().lower()
            match = re.search(r"\b(light|general|complex)\b", raw)
            verdict = match.group(1) if match else ""
            if verdict in CATEGORIES and self.models.get(verdict):
                return verdict
            if verdict in CATEGORIES:
                logger.warning(
                    "Router chose %s but pool is empty; using general", verdict
                )
            else:
                logger.warning(
                    "Router returned unexpected verdict (fallback general): %r",
                    raw,
                )
            return "general"
        except Exception as e:
            logger.error(
                "Router failed (fallback general): %s", e
            )
            return "general"

    async def chat(self, context_key: str, user_text: str) -> str:
        """Route request, call a worker model, store reply. Returns answer text."""
        answer, _category, _model = await self.chat_routed(context_key, user_text)
        return answer

    async def chat_routed(self, context_key: str, user_text: str) -> tuple:
        """Like chat(), but also returns (answer, category, model_id)."""
        if not self.enabled or not self._client:
            raise RuntimeError("AI chat is not available")

        category = await self.route_request(user_text)
        candidates = self._pick_models(category)
        if not candidates:
            raise RuntimeError("No AI models configured")

        with self._contexts_lock:
            self._ensure_context(context_key)
            self._contexts[context_key].append(
                {"role": "user", "content": user_text}
            )
            self._trim_context(context_key)
            messages = list(self._contexts[context_key])
            self._mark_dirty()

        last_error = None
        for model_id in candidates:
            try:
                response = await self._client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                )
                answer = (response.choices[0].message.content or "").strip()
                if not answer:
                    answer = "…"

                with self._contexts_lock:
                    self._contexts[context_key].append(
                        {"role": "assistant", "content": answer}
                    )
                    self._trim_context(context_key)
                    self._mark_dirty()
                logger.debug(
                    "AI reply via category=%s model=%s", category, model_id
                )
                return answer, category, model_id
            except Exception as e:
                last_error = e
                logger.error("AI model %s failed: %s", model_id, e)

        with self._contexts_lock:
            if (
                self._contexts.get(context_key)
                and self._contexts[context_key][-1].get("role") == "user"
            ):
                self._contexts[context_key].pop()
                self._mark_dirty()

        raise RuntimeError(
            f"All models failed for category={category}: {last_error}"
        )
