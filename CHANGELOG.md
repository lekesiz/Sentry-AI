# Changelog

All notable changes to Sentry-AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete module implementations (OCR, Database, API)
- OCR helper using Apple Vision Framework
- Screenshot helper for screen capture
- Database persistence with SQLAlchemy
- FastAPI REST API with full endpoints
- Integration tests suite
- Makefile for common commands
- Configuration via .env file
- Comprehensive logging system

### Changed
- Improved Analyzer with OCR fallback
- Enhanced main.py with database integration
- Updated decision engine with better error handling

### Fixed
- Import statements in all modules
- Type hints and docstrings

## [1.0.0] - 2025-10-31

### Added
- Initial project structure
- Core agents: Observer, Analyzer, Decision Engine, Actor
- Configuration management with Pydantic
- Data models for all entities
- Comprehensive documentation (README, PROJECT_PLAN, QUICKSTART)
- Test suite foundation
- Requirements and dependencies
- MIT License

[Unreleased]: https://github.com/lekesiz/Sentry-AI/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/lekesiz/Sentry-AI/releases/tag/v1.0.0
