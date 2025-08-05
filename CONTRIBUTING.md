# Contributing to Jossie Fancies

Thank you for your interest in contributing to the Jossie Fancies e-commerce platform! This document provides guidelines and information for contributors.

## 🚀 **Getting Started**

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- Basic knowledge of Django and web development

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Set up the development environment: `./build.sh`
4. Create a new branch: `git checkout -b feature/your-feature-name`

## 📋 **Development Workflow**

### 1. **Issue Tracking**
- Check existing issues before creating new ones
- Use issue templates when available
- Label issues appropriately (bug, enhancement, documentation, etc.)
- Assign yourself to issues you're working on

### 2. **Branch Naming Convention**
```
feature/short-description     # New features
bugfix/short-description      # Bug fixes
hotfix/short-description      # Critical fixes
docs/short-description        # Documentation updates
refactor/short-description    # Code refactoring
```

### 3. **Development Process**
1. **Create a new branch** from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for new functionality
4. **Run the test suite** to ensure everything passes
5. **Update documentation** if needed
6. **Commit your changes** with descriptive messages
7. **Push to your fork** and create a pull request

## 🧪 **Testing Requirements**

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific test modules
python manage.py test core.tests.ProductModelTest
python manage.py test core.tests.CartAPITest

# Run with coverage
python manage.py test --with-coverage
```

### Test Guidelines
- **All new features** must include tests
- **Bug fixes** should include regression tests
- **Maintain test coverage** above 90%
- **Write clear, descriptive test names**
- **Test both success and failure scenarios**

### Test Categories
- **Model Tests**: Test data models and their methods
- **API Tests**: Test REST API endpoints
- **View Tests**: Test template views and responses
- **Service Tests**: Test business logic services
- **Integration Tests**: Test component interactions

## 📝 **Coding Standards**

### Python/Django Standards
- Follow **PEP 8** style guidelines
- Use **meaningful variable and function names**
- Write **docstrings** for classes and complex functions
- Keep **functions small and focused**
- Use **type hints** where appropriate

```python
# Good example
def calculate_cart_total(cart_items: List[CartItem]) -> Decimal:
    """Calculate the total price for all items in the cart.
    
    Args:
        cart_items: List of cart items to calculate total for
        
    Returns:
        Total price as Decimal
    """
    return sum(item.total_price for item in cart_items)
```

### Frontend Standards
- Use **Tailwind CSS** utility classes
- Write **semantic HTML**
- Ensure **accessibility compliance** (WCAG 2.1)
- Test on **multiple browsers and devices**
- Follow **progressive enhancement** principles

### CSS Development
- Edit `static/css/input.css` for custom styles
- Use Tailwind utilities when possible
- Run `npm run dev` during development
- Build production CSS with `npm run build`

## 🎯 **Pull Request Guidelines**

### Before Submitting
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No merge conflicts with main branch
- [ ] Commits are properly formatted

### PR Template
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

### Review Process
1. **Automated checks** must pass (tests, linting)
2. **Code review** by maintainers
3. **Testing** on staging environment
4. **Approval** and merge to main branch

## 🐛 **Bug Reports**

### Before Reporting
- Check if the bug has already been reported
- Try to reproduce the issue consistently
- Test with the latest version

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Browser: [e.g., Chrome 96.0]
- Python version: [e.g., 3.11.0]
- Django version: [e.g., 5.2.4]

## Screenshots
Add screenshots if applicable
```

## ✨ **Feature Requests**

### Feature Request Template
```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other solutions you've considered

## Additional Context
Any other relevant information
```

## 📚 **Documentation Guidelines**

### Documentation Standards
- Use **clear, concise language**
- Include **code examples** where helpful
- Keep **screenshots up to date**
- Write for **different skill levels**
- **Update existing docs** when making changes

### Documentation Types
- **README.md**: Project overview and quick start
- **API Documentation**: REST API endpoints and usage
- **Development Guides**: Setup and development workflows
- **Deployment Guides**: Production deployment instructions
- **User Guides**: End-user documentation

## 🔒 **Security Guidelines**

### Security Best Practices
- **Never commit secrets** or sensitive data
- **Validate all user input**
- **Use parameterized queries** to prevent SQL injection
- **Implement proper authentication** and authorization
- **Follow OWASP guidelines**

### Reporting Security Issues
- **Do not** create public issues for security vulnerabilities
- **Email security concerns** to: security@jossiefancies.com
- **Include detailed information** about the vulnerability
- **Allow time** for the security team to address the issue

## 🎨 **Design Guidelines**

### UI/UX Standards
- Follow **existing design patterns**
- Ensure **mobile responsiveness**
- Test **accessibility features**
- Use **consistent spacing and colors**
- Follow **Jossie Fancies brand guidelines**

### Color Palette
- **Primary Orange**: #FF9A00
- **Primary Dark**: #e6870a
- **Success Green**: #059669
- **Dark Variants**: #181d24, #1f252d, #2a3038

## 🏆 **Recognition**

### Contributors
All contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **GitHub contributors page**
- **Release notes** for significant contributions
- **Annual acknowledgments**

### Contribution Types
We recognize various types of contributions:
- **Code**: Bug fixes, features, improvements
- **Documentation**: Writing, editing, translating
- **Design**: UI/UX improvements, graphics
- **Testing**: Manual testing, test case writing
- **Support**: Helping other users and contributors

## 📞 **Getting Help**

### Communication Channels
- **GitHub Issues**: For bugs and feature requests
- **Email**: jossiefancies1@gmail.com
- **Development Questions**: Create a discussion on GitHub

### Response Times
- **Critical bugs**: Within 24 hours
- **General issues**: Within 1 week
- **Feature requests**: Within 2 weeks
- **Pull requests**: Within 1 week

## 📄 **License**

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to Jossie Fancies! Your efforts help us build better e-commerce experiences for everyone.** 🙏