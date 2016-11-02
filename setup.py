import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-rest-framework-jwt-auth-proxy',
    package = 'drf_jwt_auth_proxy',
    version='0.0.3',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    description='Proxy JWT authentication requests to an authentication server.',
    long_description=README,
    url='https://github.com/lcdporto/django-rest-framework-jwt-auth-proxy',
    author='Ricardo Lobo',
    author_email='ricardolobo@lcdporto.org',
    install_requires = [
    'django>=1.9.7',
    'djangorestframework>=3.3.3',
    'requests>=2.2.1',
    'PyJWT>=1.4.0,<2.0.0'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
