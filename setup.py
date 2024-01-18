from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='agt_server', 
    version='1.0',
    author='John Wu',  # Replace with your name
    author_email='john_w_wu@brown.edu',  # Replace with your email
    description='The AGT Server is a python platform designed to run and implement game environments that autonomous agents can connect to and compete in.',  # Provide a short description
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/brown-agt/agt-server-remastered',  # Replace with the URL to your repo
    project_urls={
        "Bug Tracker": "https://github.com/brown-agt/agt-server-remastered/issues",  # Replace with your issue tracker link
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: MIT License', 
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=required,
)