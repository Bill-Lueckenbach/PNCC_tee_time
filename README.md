# Python Project to Automate Getting a Tee Time at PNCC



## 📁 Project Structure

```plaintext
📁 PNCC_tee_time/
├── 📁 src/                          # Source code (importable modules)
│   └── 📁 PNCC_tee_time             # Package directory 
│       ├── 📄 PNCC_tee_time.py      # Module file 
│       └── 📄 __init__.py           # Makes directory a package
├── 📁 tests/                        # Pytest test suite
│   └── 📄 test_PNCC_tee_time.py     # Unit Tests
├── 📁 .vscode/                      # Editor settings (pytest, GitLens, docstrings)
│   └── 📄 settings.json
├── 📄 pyproject.toml                # Project metadata + pytest config
├── 📄 .gitignore                    # Files not tracked by GitHub
├── 📄 PNCC_tee_time.code-workspace  #  
└── 📄 README.md                     # This File

```



This layout is intentionally GitLens‑friendly:
- Clear separation of source code and tests
- Predictable import paths
- Clean commit history and file‑by‑file authorship
- Ideal for template repositories and reproducible workflows

## 🚀 Getting Started



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