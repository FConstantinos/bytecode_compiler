from setuptools import setup, find_packages

setup(
    name='bytecode-compiler',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bytecode-compiler=bytecode_compiler.compiler:main',
        ],
    },
)