from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    supabase_url: str
    supabase_anon_key: str
    public_base_url: str = "http://localhost:8000"
    rate_limit_max_requests: int = 10
    rate_limit_window_seconds: int = 10
    geo_mock: bool = False
    geo_a_down: bool = False
    geo_b_down: bool = False
    geo_test_ip: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
