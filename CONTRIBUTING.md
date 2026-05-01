# Contributing to SmartLens

Thank you for your interest in contributing! This document provides guidelines for contributing to the SmartLens project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature: `git checkout -b feature/amazing-feature`
4. Follow the setup instructions in the main README.md

## Development Workflow

### Backend Development

1. Set up virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Run the backend server:
```bash
cd backend
python -m uvicorn main:app --reload
```

3. Create a new router in `backend/routers/` for new endpoints
4. Add comprehensive docstrings to your functions
5. Test with the provided test scripts

### Frontend Development

1. Edit `frontend/SmartLens_HK_Final.html` (or create a new variant)
2. Test locally by serving through Nginx
3. Clear browser cache (Cmd+Shift+R on macOS) to see changes
4. Validate API calls in browser DevTools Console

### Testing Vision Models

To test a new vision model in the Hong Kong region:

1. Use the scripts in `frontend/script.py` as a template
2. Update the model list with your candidate models
3. Run comprehensive tests to verify accuracy and speed
4. Document results in the model comparison table

## Code Style

### Python
- Follow PEP 8
- Use type hints where possible
- Maximum line length: 100 characters
- Use `black` for formatting (optional but recommended)

### JavaScript/HTML
- Use semantic HTML
- Keep styles organized in CSS sections
- Use descriptive variable names
- Add comments for complex logic

## Commit Messages

Write clear, descriptive commit messages:

```
[area] Brief description of change

More detailed explanation if needed.

- Bullet points for specific changes
- Reference issues if applicable #123
```

Example:
```
[backend] Add sleep quality AI analysis endpoint

- Implements POST /health/sleep endpoint
- Uses Llama 4 for sleep pattern analysis
- Adds Redis caching with 1-hour TTL
- Includes comprehensive error handling

Fixes #45
```

## Pull Request Process

1. Update README.md if you've added new features
2. Test your changes thoroughly locally
3. Ensure all API endpoints work correctly
4. Update .env.example if you add new configuration
5. Create a Pull Request with clear description of changes

## Testing

### Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost
- [ ] Food image analysis returns valid nutrition data
- [ ] News classification works correctly
- [ ] Redis caching is functional
- [ ] Error handling works as expected
- [ ] SSE notifications stream is active

## Reporting Issues

When reporting issues, please include:

1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. Your environment (Python version, OS, browser)
5. Error logs if applicable

## Features & Roadmap

Current focus areas:
- Vision model optimization for regional performance
- Enhanced nutrition analysis accuracy
- Real-time health insights
- Misinformation detection improvements

Feel free to discuss new ideas in Issues before starting work.

## Questions?

- Check existing Issues and PRs
- Read the main README.md thoroughly
- Create a new Discussion thread

Thank you for contributing to SmartLens! 🔮
