# Contributing to ProBharatAI

Thank you for your interest in contributing to ProBharatAI! 🎉

## How to Contribute

### 🐛 Report Bugs
- Open a [GitHub Issue](https://github.com/probharatai/probharatai/issues)
- Include your OS, Python version, and error logs

### 💡 Suggest Features
- Open a discussion or issue with the `enhancement` label
- Describe the use case and expected behavior

### 🔧 Submit Code

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/probharatai.git
   ```
3. **Create** a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make** your changes
5. **Test** your changes
6. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add voice command support"
   ```
7. **Push** and create a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

## Development Setup

```bash
# Clone
git clone https://github.com/probharatai/probharatai.git
cd probharatai

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
npm run dev
```

## Plugin Development

Want to create a plugin? Plugins live in `backend/tools/` and follow this pattern:

```python
class MyPlugin:
    def execute(self, action: str, params: dict) -> dict:
        # Your automation logic here
        return {"status": "success", "data": result}
```

Register your plugin in `backend/agents/executor.py`.

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something amazing together.

---

**Questions?** Open a discussion or reach out on our community channels!
