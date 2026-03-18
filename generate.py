import os
import yaml
import logging

from lib import substitute_tokens, flatten_dict, find_unresolved_tokens
from jinja2 import Environment, FileSystemLoader


DIR = os.path.dirname(__file__)
THEMES_DIR = 'themes'
FONTS_DIR = 'fonts'
CONFIG_DIR = 'config'
OUTPUT_DIR = 'output'
TEMPLATES_DIR = 'templates'
COLORSCHEMES_DIR = 'colorschemes'
CONFIG_PATH = os.path.join(DIR, CONFIG_DIR)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for more verbosity
    format="[%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Output to console
        # Optionally add a FileHandler:
        # logging.FileHandler("generate_configs.log")
    ]
)
logger = logging.getLogger(__name__)


def load_yaml(filename):
    with open(filename, 'r') as f: data = yaml.safe_load(f)
    logger.debug(f"YAML data loaded from {filename}: {data}")
    return data

def transform_theme(theme, tool):
    if tool == "kitty": return theme.upper()

    # Default: return the original theme
    return theme


# Load the theme variables from YAML
data = load_yaml(os.path.join(CONFIG_PATH, 'general.yml'))

theme_name = data.get('theme')
theme_file = os.path.join(CONFIG_PATH, THEMES_DIR, f'{theme_name}.yml')

# Load theme-specific configuration
if os.path.exists(theme_file):
    theme_config = load_yaml(theme_file)
else:
    raise FileNotFoundError(f"Theme file '{theme_file}' not found.")

# Load the corresponding colorscheme file
assert(not theme_config.get('colors'))
theme_config['colors'] = load_yaml(os.path.join(DIR, COLORSCHEMES_DIR, f'{theme_name}.yml'))
data['theme'] = theme_config

font_name = data.get('font')
if isinstance(font_name, str):
    font_file = os.path.join(CONFIG_PATH, FONTS_DIR, f'{font_name}.yml')
    if os.path.exists(font_file):
        data['font'] = load_yaml(font_file)
    else:
        raise FileNotFoundError(f"Font file '{font_file}' not found.")

data = substitute_tokens(data, flatten_dict(data['theme']['colors']))

# Warn about unresolved tokens
unresolved = find_unresolved_tokens(data)
for path, token in unresolved:
    logger.warning(f"Unresolved token {token} at {path}")

# Set up Jinja2 environment
template_loader = FileSystemLoader(searchpath=os.path.join(DIR, TEMPLATES_DIR))
env = Environment(loader=template_loader)

env.filters['transform_theme'] = transform_theme

# List of templates and their output files
configs = {
    "kitty/kitty.conf.j2": "kitty/kitty.conf",
    "tmux/tmux.conf.j2": "tmux/.tmux.conf",
    "tmux/theme.sh.j2": "tmux/theme.sh",
    "ipython/ipython_config.py.j2": "ipython/ipython_config.py",
    "zsh/theme.zsh-theme.j2": "zsh/theme.zsh-theme",
    "nvim/globals.lua.j2": "nvim/globals.lua",
    "nvim/colors.lua.j2": "nvim/colors.lua",
    "zellij/config.kdl.j2": "zellij/config.kdl",
    "ghostty/config.j2": "ghostty/config",
    "colorls/dark_colors.yaml.j2": "colorls/dark_colors.yaml",
    "colorls/light_colors.yaml.j2": "colorls/light_colors.yaml",
}

# Render each template and write to file
for template_name, output_path in configs.items():
    template = env.get_template(template_name)
    rendered_content = template.render(**data)

    # Ensure output directory exists
    _output_path = os.path.join(DIR, OUTPUT_DIR, output_path)
    os.makedirs(os.path.dirname(_output_path), exist_ok=True)
    with open(_output_path, "w") as out_file:
        out_file.write(rendered_content)

    logger.debug(f"Generated {OUTPUT_DIR}/{output_path}")

logger.info("All configuration files have been generated.")
