import typing
from functools import cached_property

from jwcrypto import jwk
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic Settings object - do not instantiate it directly,
    please use get_settings() as a dependency where possible"""

    model_config = SettingsConfigDict(env_nested_delimiter="__")

    SERVICE_NAME: str = "Platformics"

    # Hardcoded vars"
    DB_DRIVER: str = "postgresql+asyncpg"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 0
    DB_ECHO: bool = False
    DEBUG: bool = False

    # Pydantic automatically tries to load settings with matching names from
    # the environment if available.
    # It also supports creating more methods of fetching secrets (ex: secrets
    # manager, disk, etc) but we don't need that just yet.

    # Properties usually read from env vars
    CERBOS_URL: str
    PLATFORMICS_DATABASE_HOST: str
    PLATFORMICS_DATABASE_PORT: str
    PLATFORMICS_DATABASE_USER: str
    PLATFORMICS_DATABASE_PASSWORD: str
    PLATFORMICS_DATABASE_NAME: str
    OUTPUT_S3_PREFIX: typing.Optional[str] = None
    JWK_PUBLIC_KEY_FILE: str
    JWK_PRIVATE_KEY_FILE: str
    DEFAULT_UPLOAD_BUCKET: str
    DEFAULT_UPLOAD_PROTOCOL: str
    BOTO_ENDPOINT_URL: typing.Optional[str] = None
    AWS_REGION: str
    DB_ECHO: bool = False

    ############################################################################
    # Computed properties

    @cached_property
    def JWK_PRIVATE_KEY(self) -> jwk.JWK:  # noqa: N802
        key = None
        if not self.JWK_PRIVATE_KEY_FILE:
            raise Exception("JWK_PRIVATE_KEY_FILE not set")
        with open(self.JWK_PRIVATE_KEY_FILE) as fh:
            key = fh.read().strip()
        private_key = jwk.JWK.from_pem(key.encode("utf-8"))
        return private_key

    @cached_property
    def JWK_PUBLIC_KEY(self) -> jwk.JWK:  # noqa: N802
        key = None
        if not self.JWK_PUBLIC_KEY_FILE:
            raise Exception("JWK_PUBLIC_KEY_FILE not set")
        with open(self.JWK_PUBLIC_KEY_FILE) as fh:
            key = fh.read().strip()
        public_key = jwk.JWK.from_pem(key.encode("utf-8"))
        return public_key

    @cached_property
    def DB_URI(self) -> str:  # noqa: N802
        db_uri = "{protocol}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}".format(
            protocol=self.DB_DRIVER,
            db_host=self.PLATFORMICS_DATABASE_HOST,
            db_port=self.PLATFORMICS_DATABASE_PORT,
            db_user=self.PLATFORMICS_DATABASE_USER,
            db_pass=self.PLATFORMICS_DATABASE_PASSWORD,
            db_name=self.PLATFORMICS_DATABASE_NAME,
        )
        return db_uri

    @cached_property
    def SYNC_DB_URI(self) -> str:  # noqa: N802
        db_uri = "postgresql+psycopg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}".format(
            db_host=self.PLATFORMICS_DATABASE_HOST,
            db_port=self.PLATFORMICS_DATABASE_PORT,
            db_user=self.PLATFORMICS_DATABASE_USER,
            db_pass=self.PLATFORMICS_DATABASE_PASSWORD,
            db_name=self.PLATFORMICS_DATABASE_NAME,
        )
        return db_uri


class APISettings(Settings): ...


class CLISettings(Settings): ...
