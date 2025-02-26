import os
import yaml
import logging

from lib import substitute_tokens, flatten_dict
from jinja2 import Environment, FileSystemLoader


CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')

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
data = load_yaml(os.path.join(CONFIG_DIR, 'general.yml'))

theme_name = data.get('theme')
theme_file = os.path.join(CONFIG_DIR, 'themes', f'{theme_name}.yml')

# Load theme-specific configuration
if os.path.exists(theme_file):
    theme_config = load_yaml(theme_file)
else:
    raise FileNotFoundError(f"Theme file '{theme_file}' not found.")

# Load the corresponding colorscheme file
assert(not theme_config.get('colors'))
theme_config['colors'] = load_yaml(f'colorschemes/{theme_name}.yml')
data['theme'] = theme_config

data = substitute_tokens(data, flatten_dict(data['theme']['colors']))

# Set up Jinja2 environment
template_loader = FileSystemLoader(searchpath="./templates")
env = Environment(loader=template_loader)

env.filters['transform_theme'] = transform_theme

# List of templates and their output files
configs = {
    "kitty/kitty.conf.j2": "output/kitty/kitty.conf",
    "tmux/tmux.conf.j2": "output/tmux/.tmux.conf",
    "tmux/theme.sh.j2": "output/tmux/theme.sh",
    "ipython/ipython_config.py.j2": "output/ipython/ipython_config.py",
    "zsh/theme.zsh-theme.j2": "output/zsh/theme.zsh-theme",
    "nvim/globals.lua.j2": "output/nvim/globals.lua",
    "nvim/colorscheme.lua.j2": "output/nvim/colorscheme.lua",
    "colorls/dark_colors.yaml.j2": "output/colorls/dark_colors.yaml",
    "colorls/light_colors.yaml.j2": "output/colorls/light_colors.yaml",
    "colorls/files.yaml.j2": "output/colorls/files.yaml"
}

# Render each template and write to file
for template_name, output_path in configs.items():
    template = env.get_template(template_name)
    rendered_content = template.render(**data)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as out_file:
        out_file.write(rendered_content)

    logger.debug(f"Generated {output_path}")

logger.info("All configuration files have been generated.")
