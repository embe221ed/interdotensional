# interd•tensional

interdotensional is a Python-powered tool for managing and generating your dotfiles and configuration files. It uses a centralized YAML configuration and Jinja2 templating to ensure a unified theme across tools like Neovim, Kitty, Tmux, Zsh, and more.

## Features

- **Centralized Theme Management:** define your global settings and themes in YAML
- **Modular Configuration:** organize your settings into multiple YAML files for scalability
- **Token Substitution:** use tokens (e.g., `$blue$`) in your templates that get dynamically replaced
- **Tool-Specific Customizations:** override global settings on a per-tool basis
- **Extensible Templating:** leverage Jinja2 to generate config files for various applications

## Project Structure

```
interdotensional/
├── colorschemes/            # color scheme YAML files (e.g., x.yml, y.yml)
├── README.md                # project overview and instructions
├── config/
│   └── general.yml          # global settings and selected theme
├── themes/                  # theme-specific YAML files (e.g., x.yml, y.yml)
├── generate.py              # Python script to render Jinja2 templates using YAML data
├── requirements.txt         # Python dependencies (e.g., PyYAML, Jinja2)
├── templates/               # Jinja2 template files for each tool's configuration
│   ├── kitty/
│   │   └── kitty.conf.j2
│   ├── tmux.conf.j2
│   ├── nvim_init.lua.j2
│   ├── zshrc.j2
│   └── ...                  # additional templates as needed
└── output/                  # generated configuration files (ready to deploy)
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/embe221ed/interdotensional.git
   cd interdotensional
   ```

2. **Set Up a Virtual Environment (Optional):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Configure Settings:**
   - update `general.yml` with your global options and choose your desired theme.
   - edit or add theme YAML files in the `themes/` directory.
   - customize the Jinja2 templates in the `templates/` folder for each tool.

2. **Generate Configuration Files:**

   ```bash
   python generate.py
   ```

   this will render the templates with your configuration data and output the final files into the `output/` directory.

3. **Deploy Your Dotfiles:**
   - copy or symlink the generated configuration files from the `output/` directory to their appropriate locations on your system.

## Customization

- **Token Substitution:**  
  use tokens like `$blue$` in your templates. The tool will replace these tokens with values defined in your theme YAML files.

- **Nested Tokens:**  
  organize your YAML files to support nested tokens (e.g., `$git.add$`) by flattening the structure during processing.

- **Adding New Templates:**  
  simply add new Jinja2 template files to the `templates/` directory and update the generation script accordingly.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Disclaimer

This tool is provided as-is and is intended to serve as a starting point for managing your dotfiles. Customize it to fit your personal workflow.

Happy configuring with interdotensional!
