import sys
import scatter_daemon
from os import path
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call, CalledProcessError

pwd = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(pwd, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class LintCommand(develop):
    """ Run linting"""
    def run(self):
        try:
            check_call("flake8 --config .flake8".split())
        except CalledProcessError as err:
            if 'non-zero' in str(err):
                print("linting failed with warnings", file=sys.stderr)
                sys.exit(1)


class TestCommand(develop):
    """ Run linting"""
    def run(self):
        try:
            check_call(["pytest"])
        except CalledProcessError as err:
            if 'non-zero' in str(err):
                print("testing failed", file=sys.stderr)
                sys.exit(1)


def requirements_to_list(filename):
    return [dep for dep in open(path.join(pwd, filename)).read().split('\n') if (
        dep and not dep.startswith('#')
    )]


setup(
    name='scatter_daemon',
    version=scatter_daemon.__version__,
    description='Validation and Hosting daemon for scatter.online.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mikeshultz/scatter-daemon',
    author=scatter_daemon.__author__,
    author_email=scatter_daemon.__email__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Internet',
        'Topic :: System :: Filesystems',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='ipfs ethereum',
    packages=find_packages(exclude=['docs', 'tests', 'dist', 'build']),
    install_requires=requirements_to_list('requirements.txt'),
    extras_require={
        'dev': requirements_to_list('requirements.dev.txt'),
        #'test': requirements_to_list('requirements.test.txt'),
    },
    entry_points={
        'console_scripts': [
            'scatter=scatter_daemon.cli:main',
        ],
    },
    package_data={
        '': [
            'README.md',
            'LICENSE',
        ],
        'scatter_daemon': [
            'common/files',
        ],
    },
    cmdclass={
        'lint': LintCommand,
        'test': TestCommand,
    }
)
