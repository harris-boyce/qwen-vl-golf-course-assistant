# Contributing to Qwen-VL Golf Course Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant error messages or logs

### Suggesting Enhancements

We welcome suggestions for new features or improvements:
- Check if the enhancement has already been suggested
- Create an issue with a clear description of the enhancement
- Explain why this enhancement would be useful
- Provide examples of how it would work

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/qwen-vl-golf-course-assistant.git
   cd qwen-vl-golf-course-assistant
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed
   - Ensure all tests pass

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Provide a clear description of your changes

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write clear, descriptive docstrings
- Keep functions focused and modular

### Testing

- Add tests for new features
- Ensure existing tests pass
- Run tests before submitting:
  ```bash
  python tests/test_basic.py
  ```

### Documentation

- Update README.md if adding new features
- Add docstrings to all functions and classes
- Update GETTING_STARTED.md for user-facing changes
- Include examples in docstrings

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, etc.)
- Keep the first line under 72 characters
- Add detailed description if needed

Example:
```
Add NDVI threshold configuration option

- Allow users to customize NDVI thresholds in config
- Update documentation with threshold examples
- Add tests for custom thresholds
```

## Project Structure

```
qwen-vl-golf-course-assistant/
├── src/golf_assistant/     # Main package
│   ├── scraper/           # Web scraping module
│   ├── imagery/           # Satellite imagery module
│   ├── agent/             # AI agent module
│   ├── schemas/           # JSON schemas
│   └── utils/             # Utilities
├── examples/              # Example scripts
├── tests/                 # Test suite
├── config/                # Configuration files
└── docs/                  # Documentation (future)
```

## Areas for Contribution

We especially welcome contributions in:

### High Priority
- [ ] Implement actual USGS NAIP API integration
- [ ] Add comprehensive test suite
- [ ] Improve error handling and logging
- [ ] Add more example scripts

### Medium Priority
- [ ] Google Earth Engine integration
- [ ] Additional satellite imagery sources
- [ ] Performance optimization
- [ ] Caching improvements

### Low Priority
- [ ] Web dashboard interface
- [ ] Additional export formats
- [ ] Batch processing capabilities
- [ ] Real-time monitoring features

## Extension Points

The system is designed to be extensible:

### Adding New Scrapers
1. Subclass `WebScraper`
2. Override `extract_golf_course_info()`
3. Add site-specific extraction logic

### Adding New Imagery Sources
1. Subclass `SatelliteRetriever`
2. Implement source-specific retrieval
3. Maintain consistent output format

### Adding New Analysis Methods
1. Extend `QwenVLAgent`
2. Add custom analysis methods
3. Integrate with schema system

## Code Review Process

1. All submissions require review
2. Maintainers will review PRs within a week
3. Address any requested changes
4. Once approved, maintainer will merge

## Getting Help

- Create an issue for questions
- Check existing issues and documentation
- Be respectful and patient

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions

Thank you for contributing! 🎉
