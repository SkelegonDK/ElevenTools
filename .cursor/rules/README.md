# Streamlit Cursor Rules

This directory contains comprehensive Cursor rules for secure and efficient Streamlit development using UV package management.

## Files Overview

### 1. `streamlit-security-performance.mdc`
Core security and performance rules including:
- **Security Best Practices**: Secrets management, authentication, input validation
- **Performance Optimization**: Caching strategies, memory management, fragment optimization  
- **Code Quality**: Type hints, error handling, state management
- **UI/UX Guidelines**: Elegant design patterns, loading states, validation UI

### 2. `streamlit-components-patterns.mdc`
Advanced component patterns and techniques:
- **Component Security**: Form handling, file uploads, data visualization
- **Advanced Patterns**: Multi-page navigation, dynamic content, database integration
- **API Integration**: Retry logic, circuit breakers, rate limiting
- **Performance Patterns**: Efficient data processing, memory-optimized visualizations

### 3. `uv-streamlit-workflow.mdc`
UV-specific development workflow and best practices:
- **UV Package Management**: Project initialization, dependency management, security auditing
- **Development Workflow**: Local setup, code quality integration, testing patterns
- **CI/CD Integration**: GitHub Actions, Docker deployment, performance monitoring
- **Production Deployment**: Environment preparation, monitoring, maintenance

## Key Principles

### Security First
- Never hardcode secrets or credentials
- Always validate user inputs
- Use authentication and authorization
- Enable all security features in production

### Performance Optimized
- Use appropriate caching decorators (`@st.cache_data`, `@st.cache_resource`)
- Implement memory management for large datasets
- Use fragments for independent UI updates
- Monitor and optimize dependency resolution

### UV-Centric Workflow
- Use `uv` exclusively for package management
- Pin security-critical dependencies
- Regular security audits with `uv audit`
- Reproducible builds with lock files

### Code Quality
- Type hints for all functions
- Comprehensive error handling
- Separation of concerns
- Consistent naming conventions

## Usage

These rules are automatically loaded by Cursor when working in this repository. The rules enforce:

1. **Mandatory UV Usage**: All package management must use UV
2. **Security Requirements**: Secrets management and input validation
3. **Performance Standards**: Proper caching and memory management
4. **Code Quality**: Type hints, error handling, testing

## Integration

The rules integrate with:
- **Pre-commit hooks**: Ruff, Black, MyPy, Bandit
- **CI/CD pipelines**: GitHub Actions with security scanning
- **Testing frameworks**: pytest with Streamlit testing
- **Monitoring**: Performance and security metrics

## Anti-Patterns

The rules explicitly prohibit:
- Using pip instead of UV
- Hardcoding secrets in source code
- Missing input validation
- Not using caching for expensive operations
- Mixing package managers
- Deploying without security scanning

These rules ensure secure, performant, and maintainable Streamlit applications following modern Python development practices.