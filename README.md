# Python Project to Automate Getting a Tee Time at PNCC



## 📁 Project Structure

```plaintext
📁 PNCC_tee_time/
├── 📁 src/                          # Source code (importable modules)
│   └── 📁 PNCC_tee_time/            # Package directory
│       ├── 📄 __init__.py           # Makes directory a package
│       ├── 📄 __main__.py           # Entry point: python -m PNCC_tee_time
│       ├── 📄 automation.py         # CLI argument parsing + main workflow
│       ├── 📄 base.py               # WebDriver setup / teardown helpers
│       ├── 📄 elements.py           # Low-level element interaction helpers
│       ├── 📄 locators.py           # CSS/XPath selectors and page URLs
│       ├── 📄 pages.py              # Page-level actions (login, booking, etc.)
│       └── 📄 settings.py           # Credentials and environment config
├── 📁 tests/                        # Pytest test suite
│   ├── 📄 test_automation.py        # Unit tests for automation.py
│   ├── 📄 test_base.py              # Unit tests for base.py
│   ├── 📄 test_integration.py       # Integration/smoke tests (live browser)
│   └── 📄 test_settings.py          # Unit tests for settings.py
├── 📁 .vscode/                      # Editor settings (pytest, GitLens, docstrings)
│   └── 📄 settings.json
├── 📄 .env                          # Credentials (not tracked by Git)
├── 📄 .gitignore                    # Files not tracked by GitHub
├── 📄 pyproject.toml                # Project metadata + pytest config
├── 📄 PNCC_tee_time.code-workspace  # VS Code workspace file
└── 📄 README.md                     # This file

```




## 🚀 Getting Started


## 🪵 Logging Configuration

The app reads logging settings from environment variables in your `.env` file.

```env
# Global log level for all modules
PNCC_LOG_LEVEL=INFO

# Optional: write logs to a file
PNCC_LOG_FILE=pncc.log

# Optional: force DEBUG only for selected modules (comma-separated)
PNCC_LOG_DEBUG_MODULES=PNCC_tee_time.pages,PNCC_tee_time.date_time_utils
```

How it works:
1. `PNCC_LOG_LEVEL` sets the default level for the whole app.
2. `PNCC_LOG_DEBUG_MODULES` overrides specific module loggers to `DEBUG`.
3. This lets you keep most output at `INFO` while getting deep diagnostics for targeted modules.


## 🔧 Common Tasks

### Open a webpage with selenium in the interpreter
>>> from selenium import webdriver
>>> from selenium.webdriver.chrome.options import Options

>>> options = Options()
>>> options.add_argument("--headless")
>>> driver = webdriver.Chrome(options=options)
>>> driver.get("https://www.python.org")
>>> driver.title
'Welcome to Python.org'
>>> driver.quit()

### Add a New Module to Your Package
```bash
# Create a new .py file in your package
touch src/your_package/my_module.py

# Create a test file for it
touch tests/test_my_module.py
```

### Add a New Dependency
```bash
# Install the package
pip install package_name

# Add it to pyproject.toml
# Edit the [project] dependencies section

# Reinstall with your changes
pip install .[dev]
```

### Run Tests with Coverage
```bash
# Install coverage (add to [project.optional-dependencies] first)
pip install coverage pytest-cov

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## 🐛 Troubleshooting

### Imports like `from src.example.example import ...` fail
**Solution**: Ensure your pytest configuration in `pyproject.toml` has:
```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
```

And run pytest from the project root directory.

### `.venv` folder is large / slowing down Git
**Solution**: Ensure `.venv/` is in your `.gitignore`:
```bash
# In .gitignore
.venv/
venv/
env/
```

`.venv/` should stay local and should not be committed as part of a project template.

### `python -m venv .venv` fails because files already exist or are in use
**Solution**: This usually means `.venv/` already exists or one of its files is locked.

```bash
# Use the existing environment
# Activate it instead of recreating it
```

If you want to recreate it:
1. Close terminals or tools that are using `.venv`
2. Delete `.venv/`
3. Run `python -m venv .venv` again

### Virtual environment not activating on Windows
**Solution**: If the activation script fails, try:
```powershell
# Allow script execution (one-time)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.venv\Scripts\Activate.ps1
```

### Changes to pyproject.toml not taking effect
**Solution**: Reinstall the package in editable mode:
```bash
pip install -e .[dev]
```

## 📚 Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [PEP 517 - Python packaging build backend specification](https://www.python.org/dev/peps/pep-0517/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [VS Code Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [[Modern Web Automation With Python and Selenium] 
  (https://realpython.com/modern-web-automation-with-python-and-selenium/#understand-the-project-and-approach)

## 📦 Dependencies

- Python (any modern version)
- Selenium
- pytest (installed via pip)
- VS Code extensions:
  - Python
  - Pylance
  - GitLens
  - Jupyter
  - autoDocstring

## 🎯 Purpose
Log in and get a tee time at PNCC

## 📜 License

You may use, modify, or extend this template freely.