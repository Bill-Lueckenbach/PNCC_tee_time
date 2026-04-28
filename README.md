# Python Project Template (VS Code • Pytest • GitLens • Google Docstrings)

A clean, minimal, and fully reproducible Python project template designed for use with VS Code. Includes pytest, Google‑style docstrings, GitLens‑optimized structure, and a workspace file for instant setup.

## 📁 Project Structure

```plaintext
📁 my_project/
├── 📁 src/                          # Source code (importable modules)
│   └── 📁 example                   # Package directory --- RENAME THIS ---
│       ├── 📄 example.py            # Module file --- RENAME THIS ---
│       └── 📄 __init__.py           # Makes directory a package
├── 📁 tests/                        # Pytest test suite
│   └── 📄 test_example.py           # --- RENAME THIS ---
├── 📁 .vscode/                      # Editor settings (pytest, GitLens, docstrings)
│   └── 📄 settings.json
├── 📄 pyproject.toml                # Project metadata + pytest config
├── 📄 .gitignore                    # Files not tracked by GitHub
├── 📄 example.code-workspace        #  --- RENAME THIS ---
└── 📄 README.md                     # This File

```



This layout is intentionally GitLens‑friendly:
- Clear separation of source code and tests
- Predictable import paths
- Clean commit history and file‑by‑file authorship
- Ideal for template repositories and reproducible workflows

## 🚀 Getting Started

### 1. Create Your Project from This Template

1. Open your browser and go to **[GitHub](https://github.com)**
2. **Log in to your GitHub account** (create one if needed)
3. Navigate to **[this template repository](https://github.com/bill-lueckenbach/new_project_template)**
4. Click the **"Use this template"** button (green button near the top right)
5. Select **"Create a new repository"**
6. Name your repository (e.g., `my-awesome-project`)
7. Choose visibility (public or private)
8. Click **"Create repository from template"**

### 2. Clone to Your Local Machine and Open in VS Code

Important: Open the `.code-workspace` file (not just the folder) so all template settings and views load correctly.

1. Open **VS Code**
2. Press **Ctrl+Shift+P** (or **Cmd+Shift+P** on Mac)
3. Type **"Git: Clone"** and select it
4. Paste your repository URL: `https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git`
5. Select a folder to clone into
6. Click **Open Repository** in the prompt (or open the cloned folder manually)
7. In the top menu, click **File → Open Workspace from File...**
8. Select `example.code-workspace`
9. If you renamed the workspace file, select your renamed `.code-workspace` file instead

- This loads the optimized workspace configuration with all recommended settings

### 3. Set Up Your Python Environment

Open a terminal in VS Code (**Ctrl+`** or Terminal → New Terminal) and run:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies (including dev tools)
pip install .[dev]
```

VS Code will likely prompt you to select the Python interpreter—choose the one in `.venv/`.

Notes:
- `.venv/` is a local virtual environment for your machine only. Do not commit it to git.
- Create `.venv` once per clone of the repository.
- If `.venv` already exists, activate it and continue. Do not rerun `python -m venv .venv` unless you are intentionally recreating the environment.
- If you need a fresh environment, delete `.venv/`, then run `python -m venv .venv` again.

### 4. Customize for Your Project

1. **Rename the workspace file**: `example.code-workspace` → `your_project_name.code-workspace`

2. **Customize the source package**:
   - Rename `src/example/` → `src/your_package_name/`
   - Rename `src/your_package_name/example.py` → `src/your_package_name/your_module.py`
   - Update imports in test files accordingly

3. **Update configuration**:
   - Edit `pyproject.toml`:
     - Change `name = "my_project"` to your project name
     - Update `version`, `description`, `authors`, and `keywords`
   - Update `.github/workflows/` if you have CI/CD configured

4. **Update test imports**:
   - Change `from src.example.example import add` to match your actual module structure

5. **Update README.md**:
   - Replace this section with your project description
   - Update installation and usage instructions for your specific project

## 🧪 Running Tests

### VS Code
- Open the Testing panel (beaker icon)
- Click Run All Tests

### Terminal
pytest

Pytest is configured through `pyproject.toml`:

[tool.pytest.ini_options]
pythonpath = ["src"]

This ensures imports like `from src.example.example import add` work without extra path hacks.

## 📝 Example Code (Google Docstrings)

### src/example/example.py
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The sum of `a` and `b`.

    Raises:
        TypeError: If either argument is not an integer.
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers.")
    return a + b

## 🧪 Example Test

### tests/test_example.py
from src.example.example import add

def test_add():
    """Test that add() returns the correct sum."""
    assert add(2, 3) == 5

## ⚙️ VS Code Configuration

`.vscode/settings.json` enables:
- pytest
- GitLens line + file history
- Google‑style docstring generation
- Clean file tree (hides `__pycache__` and `.pyc` files)

The workspace file (`example.code-workspace`) also:
- Loads recommended extensions
- Applies consistent settings across machines
- Keeps the environment reproducible

## 🚀 Quick Reference

### Update pyproject.toml for Your Project
```toml
[project]
name = "your_project_name"          # Change this
version = "0.1.0"                   # Your version
description = "Your project desc"   # Your description
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
keywords = ["your", "keywords"]     # Your keywords
```

### Environment Variables (Optional)
Create a `.env` file at the project root for local development:
```bash
# .env
PYTHONPATH=src
```

This file can be loaded by your IDE or shell for consistent configuration.

## 🧭 Template Philosophy

This template is designed to be:
- **Minimal**: No unnecessary dependencies or complexity
- **Reproducible**: Same setup across all machines and developers
- **Scalable**: Easy to extend with additional packages and modules
- **GitLens-friendly**: Clean structure for version control and blame views
- **Python-idiomatic**: Follows Python packaging best practices (PEP 517, PEP 518)

## 🐙 Using as a GitHub Template

### What Gets Included When Using "Use This Template"
When you use the GitHub "Use this template" button, you get:
- ✅ All source code and configuration files
- ✅ All tests and test configuration
- ✅ VS Code workspace and settings
- ✅ `pyproject.toml` (update this for your project!)
- ✅ This README (update this too!)
- ❌ Git history (fresh start with your own history)
- ❌ Issues, pull requests, or discussions from the original

### After Creating Your Repository
Your new repository will:
1. Start with a clean Git history
2. Retain all the template structure and configuration
3. Be completely independent from this template
4. Allow you to make commits without affecting the original template

## 🔧 Common Tasks

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

## 📦 Dependencies

This template intentionally keeps dependencies minimal:

- Python (any modern version)
- pytest (installed via pip)
- VS Code extensions:
  - Python
  - Pylance
  - GitLens
  - Jupyter
  - autoDocstring

## 🎯 Purpose

This template is ideal for:
- Small utilities
- Prototypes
- Teaching and onboarding
- GitHub template repositories
- Reproducible workflows
- Clean GitLens‑visible commit history

## 📜 License

You may use, modify, or extend this template freely.