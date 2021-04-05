from setuptools import setup, find_packages
from psread.psread import VERSION, PROJECT_URL

with open('README.rst') as file:
    long_description = file.read()

requires = [
    'boto3',
    'argcomplete',
    'appdirs'
]

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
]

setup(
    name='psread',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=find_packages(),
    url=PROJECT_URL,
    description='Quick, simple AWS Parameter Store CLI for listing/reading '
                'params with tab completion',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    install_requires=requires,
    keywords="aws parameter-store aws-parameter-store secrets",
    classifiers=classifiers,
    entry_points={
        'console_scripts': [
            'psread = psread.psread:main'
        ]
    }
)
