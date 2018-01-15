from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='codepass_web',
    packages=['codepass_web'],
    include_package_data=True,
    install_requires=required,
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
