import time
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.observability.metrics import metrics


class ModelGateway:

    def __init__(self):

        if not settings.openai_api_key:

            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )

        self.default_model = (
            settings.openai_model
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> dict[str, Any]:

        selected_model = (
            model or self.default_model
        )

        start_time = time.perf_counter()

        try:

            response = (
                await self.client.chat.completions.create(
                    model=selected_model,
                    temperature=temperature,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        },
                    ],
                )
            )

        except Exception as exc:

            metrics.error(
                type(exc).__name__
            )

            raise

        latency = (
            time.perf_counter()
            - start_time
        )

        choice = response.choices[0]
        usage = response.usage

        prompt_tokens = (
            usage.prompt_tokens
            if usage
            else 0
        )

        completion_tokens = (
            usage.completion_tokens
            if usage
            else 0
        )

        total_tokens = (
            usage.total_tokens
            if usage
            else 0
        )

        metrics.llm_request(
            latency=latency,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        return {
            "model": selected_model,
            "content": (
                choice.message.content or ""
            ),
            "finish_reason": (
                choice.finish_reason
            ),
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
            "latency_seconds": round(
                latency,
                4,
            ),
        }