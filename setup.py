from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='agt_server', 
    version='1.0',
    author='John Wu', 
    author_email='john_w_wu@brown.edu', 
    description='The AGT Server is a python platform designed to run and implement game environments that autonomous agents can connect to and compete in.',  # Provide a short description
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/brown-agt/agt-server-remastered',  
    project_urls={
        "Bug Tracker": "https://github.com/brown-agt/agt-server-remastered/issues",  
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires='>=3.6',
    install_requires=required,
)