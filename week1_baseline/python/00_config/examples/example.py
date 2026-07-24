import os
from pathlib import Path

os.environ.setdefault(
    "BOUKENSHA_DIR",
    str((Path(__file__).parent / "../../../.boukensha").resolve()),
)

from boukensha import Config, Player
from boukensha.config import Config as BConfig

config = Config()
player_settings = config.tasks("player")

print("=== Boukensha Step 0: Configuration ===")
print()
print(f"Config dir:     {config.dir}")
print(f"Tasks:          {', '.join(config.tasks().keys())}")
print()
print("-- player task --")
print(f"Provider:       {Player.provider(player_settings)}")
print(f"Model:          {Player.model(player_settings)}")
print(f"Prompt override?{str(Player.prompt_override(player_settings, 'system')).lower()}")
system_prompt = Player.system_prompt(
    player_settings,
    user_prompts_dir=config.user_prompts_dir,
    default_prompts_dir=str(BConfig.PROMPTS_DIR),
)
print(f"System prompt:  {system_prompt[:60] if system_prompt else None}...")
print()
print(f"MUD host:       {config.mud_host}:{config.mud_port}")
print(f"MUD user:       {config.mud_username}")
print()
print(f"API key set?    {str(os.environ.get('ANTHROPIC_API_KEY') is not None).lower()}")
print()
print(config)
