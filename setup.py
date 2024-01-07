from setuptools import setup, find_packages

setup(
    name="BudgetingApp",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Add your project dependencies here
        # e.g., 'PyQt5',
    ],
    entry_points={
        'console_scripts': [
            'budgetingapp = budgetingapp.main:main',
        ],
    },
    # Additional metadata about your package
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple budgeting application",
    license="MIT",
    keywords="budget finance",
    url="http://example.com/BudgetingApp",   # project home page, if any
)
