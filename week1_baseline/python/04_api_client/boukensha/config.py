import os
import yaml
from pathlib import Path
from dotenv import load_dotenv


class Config:
    DEFAULT_DIR = Path.home() / ".boukensha"
    PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

    def __init__(self):
        self.dir = self._resolve_dir()
        self._load_env()
        self.settings = self._load_settings()

    def tasks(self, name=None):
        all_tasks = self._dig("tasks") or {}
        if name is None:
            return all_tasks
        return all_tasks.get(str(name))

    @property
    def user_prompts_dir(self):
        return Path(self.dir) / "prompts"

    @property
    def mud_host(self):
        return self._dig("mud", "host") or "localhost"

    @property
    def mud_port(self):
        return self._dig("mud", "port") or 4000

    @property
    def mud_username(self):
        return self._dig("mud", "username")

    @property
    def mud_password(self):
        return self._dig("mud", "password")

    def _dig(self, *keys):
        node = self.settings
        for key in keys:
            if isinstance(node, dict):
                node = node.get(str(key))
            else:
                return None
        return node

    def _resolve_dir(self):
        raw = os.environ.get("BOUKENSHA_DIR") or str(self.DEFAULT_DIR)
        return str(Path(raw).expanduser().resolve())

    def _load_env(self):
        env_file = Path(self.dir) / ".env"
        if env_file.exists():
            load_dotenv(env_file)

    def _load_settings(self):
        settings_file = Path(self.dir) / "settings.yaml"
        if settings_file.exists():
            return yaml.safe_load(settings_file.read_text()) or {}
        return {}

    def __str__(self):
        return f"#<Boukensha::Config dir={self.dir} tasks={','.join(self.tasks().keys())}>"

    def __repr__(self):
        return self.__str__()
