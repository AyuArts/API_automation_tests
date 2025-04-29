from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field, root_validator


class Logger(BaseModel):
    debug: bool = False
    logs_dir: Path = Field(default_factory=lambda: Path("logs"))
    default_log_path: Path = None

    log_format_console: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    log_format_file: str = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
        "{name}:{function}:{line} - {message}"
    )

    class Config:
        arbitrary_types_allowed = True

    @root_validator(pre=True)
    def setup_paths(cls, values):
        logs_dir = values.get("logs_dir") or Path("logs")
        logs_dir.mkdir(exist_ok=True, parents=True)
        values["logs_dir"] = logs_dir
        values["default_log_path"] = logs_dir / "app.log"
        return values

    def configure(self):
        log_level = "DEBUG" if self.debug else "INFO"
        logger.remove()

        logger.add(
            sink=lambda msg: print(msg, end=""),
            level=log_level,
            format=self.log_format_console,
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

        logger.add(
            str(self.default_log_path),
            level=log_level,
            format=self.log_format_file,
            rotation="10 MB",
            retention="10 days",
            compression="zip",
            encoding="utf-8",
            enqueue=True,
            backtrace=True,
            diagnose=True,
        )

    def get_logger(self, name: str = "default"):
        self.configure()

        module_log_file = self.logs_dir / f"{name}.log"

        logger.add(
            str(module_log_file),
            level="DEBUG",
            format="{time} | {level} | {message}",
            rotation="5 MB",
            retention="5 days",
            compression="zip",
            encoding="utf-8",
        )

        return logger.bind(module=name)
