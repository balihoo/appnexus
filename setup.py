from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='python_appnexus_sdk',
    version='1.0',
    description='Python SDK for the AppNexus API',
    long_description=long_description,
    url='https://github.com/balihoo/appnexus',
    author='Balihoo',
    author_email='devall@balihoo.com',
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='appnexus api sdk',
    packages=['appnexus'],
    install_requires=['requests', 'python-memcached'],
    extras_require={},
    package_data={ },
    data_files=[],
    entry_points={}
)
