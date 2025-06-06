from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='tokenviz',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'tiktoken>=0.4.0',
        'click>=8.0.0',
    ],
    entry_points={
        'console_scripts': [
            'tokenviz=tokenviz.cli:main'
        ]
    },
    description='Visualize token usage in your prompts for OpenAI models',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='TokenViz Contributors',
    author_email='mattbusel@gmail.com',
    url='https://github.com/Mattbusel/tokenviz',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: General',
        'Topic :: Utilities',
    ],
    keywords='tokens, openai, gpt, visualization, cli, prompt-engineering',
    python_requires='>=3.8',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/tokenviz/issues',
        'Source': 'https://github.com/Mattbusel/tokenviz',
    },
