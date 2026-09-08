"""
Multi-Provider LLM Gateway for Niyukti HRMS.
Supports primary Google Gemini (gemini-1.5-flash / gemini-2.0-flash) with
resilient fallback to Groq (llama-3.1-70b-versatile / mixtral-8x7b-32768).
"""

from __future__ import annotations

import logging
import os
from typing import Any, AsyncIterator, Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("hrms.agents.llm_gateway")

# Environment Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PRIMARY_PROVIDER = os.getenv("AI_PRIMARY_PROVIDER", "gemini").lower()
DEFAULT_MODEL = os.getenv("AI_DEFAULT_MODEL", "gemini-3.6-flash")


class ResilientLLMGateway:
    """
    Unified gateway that provides chat completions and streaming tokens
    with automatic provider failover.
    """

    def __init__(
        self,
        primary_provider: str = PRIMARY_PROVIDER,
        default_model: str = DEFAULT_MODEL,
        temperature: float = 0.1,
    ):
        self.primary_provider = primary_provider
        self.default_model = default_model
        self.temperature = temperature

    def get_langchain_llm(self, streaming: bool = True):
        """
        Returns a LangChain-compatible chat model for LangGraph integration.
        Attempts Gemini first; falls back to Groq if Gemini is unavailable.
        """
        if self.primary_provider == "gemini" and GEMINI_API_KEY:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                return ChatGoogleGenerativeAI(
                    model=self.default_model,
                    google_api_key=GEMINI_API_KEY,
                    temperature=self.temperature,
                    streaming=streaming,
                    max_retries=2,
                )
            except Exception as e:
                logger.warning(f"Failed to instantiate ChatGoogleGenerativeAI: {e}. Falling back to Groq.")

        # Fallback to Groq if installed / configured
        if GROQ_API_KEY:
            try:
                from langchain_groq import ChatGroq

                return ChatGroq(
                    model_name="openai/gpt-oss-20b",
                    groq_api_key=GROQ_API_KEY,
                    temperature=self.temperature,
                    streaming=streaming,
                )
            except Exception as e:
                logger.warning(f"Failed to instantiate ChatGroq via LangChain: {e}")

        return None

    async def astream_chat(
        self,
        messages: list[dict[str, str]],
        system_instruction: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Asynchronously streams completion tokens from the primary provider,
        falling back to Groq if the primary provider raises an error.
        """
        provider = self.primary_provider

        # Attempt 1: Primary (Gemini)
        if provider == "gemini" and GEMINI_API_KEY:
            try:
                async for token in self._stream_gemini(messages, system_instruction):
                    yield token
                return
            except Exception as err:
                logger.error(f"Gemini streaming failed: {err}. Triggering Groq fallback.", exc_info=True)

        # Attempt 2: Fallback (Groq)
        if GROQ_API_KEY:
            try:
                async for token in self._stream_groq(messages, system_instruction):
                    yield token
                return
            except Exception as err:
                logger.error(f"Groq streaming fallback also failed: {err}", exc_info=True)

        # Emergency Fallback if both fail / rate-limited
        yield "I encountered a transient connection issue communicating with the AI reasoning gateway. Please retry your query."

    async def _stream_gemini(
        self,
        messages: list[dict[str, str]],
        system_instruction: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Direct Gemini streaming using google.genai SDK."""
        from google import genai
        import asyncio

        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt_parts = []
        if system_instruction:
            prompt_parts.append(f"[SYSTEM INSTRUCTION: {system_instruction}]\n\n")

        for m in messages:
            role_prefix = "User" if m.get("role") in ("user", "human") else "Assistant"
            prompt_parts.append(f"{role_prefix}: {m.get('content', '')}\n")

        full_prompt = "".join(prompt_parts)

        # Use sync generator in thread pool for async consumption
        def get_stream():
            return client.models.generate_content_stream(
                model="gemini-3.6-flash",
                contents=full_prompt,
            )

        loop = asyncio.get_event_loop()
        stream = await loop.run_in_executor(None, get_stream)

        for chunk in stream:
            if hasattr(chunk, "text") and chunk.text:
                yield chunk.text

    async def _stream_groq(
        self,
        messages: list[dict[str, str]],
        system_instruction: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Direct Groq streaming via groq package."""
        from groq import AsyncGroq

        client = AsyncGroq(api_key=GROQ_API_KEY)
        groq_msgs = []
        if system_instruction:
            groq_msgs.append({"role": "system", "content": system_instruction})
        for m in messages:
            groq_msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})

        stream = await client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=groq_msgs,
            temperature=self.temperature,
            stream=True,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": groq_msgs,
                "temperature": self.temperature,
                "stream": True,
            }
            async with httpx.AsyncClient(timeout=40.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        raise RuntimeError(f"Groq API returned HTTP {response.status_code}")

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            raw = line[6:].strip()
                            if raw == "[DONE]":
                                break
                            if raw:
                                try:
                                    parsed = json.loads(raw)
                                    choices = parsed.get("choices", [])
                                    if choices and choices[0].get("delta", {}).get("content"):
                                        yield choices[0]["delta"]["content"]
                                except Exception:
                                    pass


# Singleton instance
default_gateway = ResilientLLMGateway()
