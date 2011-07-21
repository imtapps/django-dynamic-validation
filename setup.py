from setuptools import setup, find_packages

from dynamic_validation import VERSION

REQUIREMENTS = [
    'django',
    'django-fields',
    'django-admin-ext',
    'django-autoload',
]

TEST_REQUIREMENTS = [
    'mock'
]

setup(
    name="django-dynamic-validation",
    version=VERSION,
    author="Matthew J. Morrison & Aaron Madison",
    author_email="mattjmorrison@mattjmorrison.com",
    description="Define user generated validation requirements for django models.",
    long_description=open('README.txt', 'r').read(),
    url="https://github.com/imtapps/django-dynamic-validation",
    packages=find_packages(exclude=['example']),
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    test_suite='runtests.runtests',
    zip_safe=False,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    dependency_links = (
        'https://bitbucket.org/twanschik/django-autoload/get/tip.tar.gz#egg=django-autoload',
    )
)