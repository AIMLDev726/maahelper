# Changelog

All notable changes to MaaHelper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-26

### 🎉 Production Release
- **First stable release** of MaaHelper
- **Production-ready** codebase with comprehensive testing
- **Full PyPI deployment** with automated CI/CD

### Fixed
- **Workflow Engine**: Fixed critical runtime errors in workflow state management
  - Added missing `definition` field to WorkflowState dataclass
  - Fixed undefined variable references in workflow execution
  - Improved workflow resume functionality with proper dataclass hydration
  - Added recursive datetime serialization for complex workflow state
- **CLI Entry Points**: Verified all CLI commands work correctly
  - `maahelper-workflow` and `maahelper-ide` entry points functional
  - All pyproject.toml script mappings validated
- **File Handler API**: Confirmed all expected methods are present and working
  - `is_supported_file()`, `detect_language()`, `scan_workspace()`, `analyze_file()`

### Improved
- **Package Structure**: Cleaned up repository for production deployment
  - Removed development/testing artifacts
  - Updated MANIFEST.in for proper packaging
  - Enhanced .gitignore for cleaner repository
- **Documentation**: Updated all version references to 1.0.0
- **Deployment**: Added automated deployment scripts and GitHub Actions

### Infrastructure
- **CI/CD Pipeline**: Complete GitHub Actions workflow
  - Multi-platform testing (Ubuntu, Windows, macOS)
  - Python 3.8-3.12 compatibility testing
  - Automated PyPI deployment on release
  - Security scanning with safety and bandit
- **Deployment Tools**: Added deployment script for easy PyPI publishing

## [0.0.5] - 2025-08-26

### Added
- **Custom Agent Prompts (Vibecoding)**: Specialized AI workflows for coding tasks
  - `prompts` - List all available custom prompts
  - `prompt-categories` - Show prompt categories
  - `code-review` - Comprehensive AI-powered code review
  - `bug-analysis` - Deep bug analysis and solutions
  - `architecture-design` - System architecture guidance
  - `implement-feature` - Complete feature implementation
  - `refactor-code` - Code refactoring assistance
  - `explain-concept` - Programming concept explanations
  - `optimize-performance` - Performance optimization analysis

- **Enhanced Model Discovery**: Improved filtering for chat completion models only
  - Filters out TTS models (Whisper), image generation (DALL-E), embeddings
  - Provider-specific filtering for OpenAI, Groq, Google, Anthropic
  - Clear user feedback on filtered models

- **Improved CLI Experience**:
  - Fixed duplicate AI message issue in command processing
  - Enhanced help documentation with new features
  - Better error handling and user feedback
  - Updated welcome messages and command listings

- **Bug Fixes and Improvements**:
  - Fixed StreamlinedFileHandler missing methods (`show_supported_files_table`, `list_supported_files`)
  - Fixed real-time analysis async/thread coordination issues
  - Fixed multiple `analyze-start` triggers with proper cleanup
  - Fixed entry point configuration for proper `--help` and `--version` handling
  - Fixed import issues when running as installed package
  - Centralized version management across all components

### Changed
- **Model Filtering**: Only chat completion models are now shown to users
- **Command Processing**: Improved command handling to prevent duplicate responses
- **Version Management**: All version strings now reference central `__version__`
- **Password Verification**: Enhanced security with immediate validation

### Fixed
- Entry point configuration pointing to correct CLI handler
- Relative import issues in installed environments
- Real-time analysis RuntimeError with event loops
- Duplicate AI responses for git commands
- Model discovery showing inappropriate models for chat completion

### Technical Improvements
- Enhanced async/thread coordination in file watching
- Improved error handling across all modules
- Better resource cleanup and memory management
- Comprehensive test coverage for new features

## [0.0.4] - Previous Release

### Added
- Initial release with basic AI assistant functionality
- Multi-provider support (OpenAI, Groq, Anthropic, Google, Ollama)
- File analysis and workspace integration
- Git integration features
- Real-time code analysis
- Dynamic model discovery

---

## Release Notes

### For Developers
- All new features are backward compatible
- API changes are minimal and well-documented
- Enhanced error handling provides better debugging information

### For Users
- New custom agent prompts provide specialized AI workflows
- Improved model selection with better filtering
- Enhanced CLI experience with clearer help and feedback
- Better performance and reliability

### Upgrade Instructions
1. Update to the latest version: `pip install --upgrade maahelper`
2. Run `maahelper --help` to see new features
3. Try the new custom prompts with `prompts` command
4. Explore specialized workflows like `code-review` and `bug-analysis`
