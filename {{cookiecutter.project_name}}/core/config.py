import logging
import os
from enum import Enum
from functools import lru_cache
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from pydantic import BaseSettings, SecretStr

load_dotenv()

logger = logging.getLogger(__name__)

class EnvironmentEnum(str, Enum):
    production = "production"
    local = "local"
    devel = "devel"
    staging = "staging"


class GlobalConfig(BaseSettings):
    """Global configurations."""
    class Config:
        case_sensitive = True


class LocalConfig(GlobalConfig):
    """Local configurations."""

    debug: bool = True
    environment: EnvironmentEnum = EnvironmentEnum.local


class DevelConfig(GlobalConfig):
    """Devel configurations."""

    debug: bool = True
    environment: EnvironmentEnum = EnvironmentEnum.devel


class StagingConfig(GlobalConfig):
    """Staging configurations."""

    debug: bool = True
    environment: EnvironmentEnum = EnvironmentEnum.staging


class ProdConfig(GlobalConfig):
    """Production configurations."""

    debug: bool = False
    environment: EnvironmentEnum = EnvironmentEnum.production


class FactoryConfig:
    def __init__(self, environment: Optional[str]):
        self.environment = environment
        self.configurations_maps = {
            EnvironmentEnum.local.value: LocalConfig,
            EnvironmentEnum.devel.value: DevelConfig,
            EnvironmentEnum.staging.value: StagingConfig,
            EnvironmentEnum.production.value: ProdConfig,
        }

    def __call__(self) -> GlobalConfig:
        return self.configurations_maps[self.environment]()


@lru_cache()
def get_configuration() -> GlobalConfig:
    return FactoryConfig(os.environ.get("ENVIRONMENT"))()


settings = get_configuration()

if settings.environment != EnvironmentEnum.production.value:
    print(f"Loaded config {settings.environment}")
