from setuptools import setup

setup(
    name='pynanoleaf',
    version='0.0.2',
    author='Marco Orovecchia',
    author_email='pynanoleaf@marco.orovecchia.com',
    url='https://github.com/Oro/pynanoleaf',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    description='A Python3 wrapper for the Nanoleaf API',
    install_requires=['requests'],
    packages=['pynanoleaf'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation",
        "Operating System :: OS Independent",
    ]
)
