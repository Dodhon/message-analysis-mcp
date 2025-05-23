# Contributing

Thanks for your interest! This project analyzes iMessage data locally through MCP.

## Setup

1. Fork and clone the repo
2. `pip install -r requirements.txt`
3. Grant Full Disk Access (see README)
4. Test: `python3 main.py`

## Project Structure
```
├── main.py              # CLI interface
├── message_analyzer.py  # Core analysis logic
├── mcp_server.py       # MCP server
├── setup_claude.py     # Auto setup
└── requirements.txt    # Dependencies
```

## Guidelines

**Code Style**
- Follow PEP 8
- Add docstrings
- Keep functions small
- Comment complex logic

**Privacy First**
- Never log message content
- No network requests
- Process and discard data
- Don't expose personal data in errors

## Bug Reports

Include:
- macOS version
- Python version  
- Error message (remove personal data)
- Steps to reproduce

## Feature Requests

Current priorities:
- Date range filtering
- Better error messages
- Performance improvements
- Contact name mapping (PRs very welcome!)

## Security Rules

**Acceptable:**
- Local processing improvements
- Better error handling
- New analysis features
- Performance optimizations

**Not Acceptable:**
- Network requests
- Data persistence beyond memory
- Logging message content
- Weakening privacy

## Pull Requests

1. Create an issue first for big changes
2. Fork and create feature branch
3. Test thoroughly
4. Update docs if needed
5. Submit PR with clear description

## License

MIT License - contributions will be licensed the same way. 