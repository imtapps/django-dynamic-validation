import os
import re
from distutils.core import Command, setup
from setuptools import find_packages

from dynamic_validation import VERSION

REQUIREMENTS = [
    'django<1.5.0',
    'django-fields',
    'django-autoload',
    'django-dynamic-rules>=0.2.0',
]

TEST_REQUIREMENTS = [
    'mock',
    'pep8',
    'pyflakes',
    'coverage',
    'django_nose',
    'nosexcover',
]

def do_setup():
    setup(
        name="django-dynamic-validation",
        version=VERSION,
        author="IMT Computer Services",
        author_email="webadmin@imtapps.com",
        description="Define user generated validation requirements for django models.",
        long_description=open('README.txt', 'r').read(),
        url="https://github.com/imtapps/django-dynamic-validation",
        packages=find_packages(exclude=['example']),
        install_requires=REQUIREMENTS,
        tests_require=TEST_REQUIREMENTS,
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
        ),
        cmdclass={
            'install_dev':InstallDependencies,
        }
    )

class InstallDependencies(Command):
    """
    Command to install both develop dependencies and test dependencies.

    Not sure why we can't find a built in command to do that already
    in an accessible way.
    """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_test_dependencies(self):
        """
        replace all > or < in the dependencies so the system does not
        try to redirect stdin or stdout from/to a file.
        """
        command_line_deps = ' '.join(REQUIREMENTS + TEST_REQUIREMENTS)
        return re.sub(re.compile(r'([<>])'), r'\\\1', command_line_deps)

    def run(self):
        os.system("pip install %s" % self.get_test_dependencies())


if __name__ == '__main__':
    do_setup()
