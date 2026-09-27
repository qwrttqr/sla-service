from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    yandex_geocoder_api_key: SecretStr          # no default: app fails at startup if missing
    osrm_car_url: str = "http://localhost:5000"
    osrm_bicycle_url: str = "http://localhost:5001"
    osrm_foot_url: str = "http://localhost:5002"
    traffic_profile_path: Path = Path("data/traffic_profile.json")

settings = Settings()