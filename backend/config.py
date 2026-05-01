from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # OpenRouter
    openrouter_api_key:       str   = ""
    openrouter_vision_model:  str   = "google/gemini-2.0-flash-001"
    openrouter_fallback_model:str   = "openai/gpt-4o-mini"
    openrouter_text_model:    str   = "google/gemini-2.0-flash-001"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # App
    app_name:             str = "SmartLens"
    daily_calorie_goal:   int = 2000
    log_level:            str = "info"

settings = Settings()
