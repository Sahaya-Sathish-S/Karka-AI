# Karka AI Doubt Assistant

This version adds a floating robot/question-mark assistant to the Karka AI website.

## Features
- Premium animated chatbot popup on the home, courses, course-detail and enrollment pages.
- OpenRouter integration is server-side; the browser never receives the API key.
- Multilingual text chat and browser speech input/output for English, Tamil, Hindi, Malayalam, Telugu, Kannada, Marathi and Bengali.
- Voice recording is tap-to-record: the microphone is off by default, records one question after the learner taps **Record**, then switches itself off. Tapping **Stop** ends it earlier.
- Karka-specific system knowledge is injected into the AI prompt: courses, career tracks, internship, four job-ready pillars, Pay After Placement, placement support, career calls and contact details.
- Local knowledge answers for common Karka questions reduce API usage.
- Short-lived answer cache reduces repeated API calls.
- Per-client request pacing and rate protection help prevent accidental API spikes.
- If OpenRouter is unavailable, the assistant falls back to a safe local response instead of breaking the website.

## OpenRouter setup
1. Create an OpenRouter API key.
2. Set `OPENROUTER_API_KEY` on the server as an environment variable. Do not hard-code it in HTML/JS.
3. The default model is `openrouter/free`. You may set `OPENROUTER_MODEL` to another OpenRouter model available to your account.
4. Optional `OPENROUTER_FALLBACK_MODELS` accepts a comma-separated list. It is intentionally empty by default so the site does not silently create paid usage.
5. Restart Flask.

Example:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
export OPENROUTER_MODEL="openrouter/free"
python app.py
```

## About limits
There is no legitimate way for a website to bypass OpenRouter/provider quotas. This implementation uses caching, local Karka answers, request pacing, and a fallback response to make the assistant last longer and degrade gracefully. OpenRouter's current limits and pricing should be checked in its dashboard/docs before production deployment.

## Voice note
Speech recognition and speech synthesis are browser capabilities. The microphone is requested only when the learner taps **Record**, and it is never left listening in the background.
