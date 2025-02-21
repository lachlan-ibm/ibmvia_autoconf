import os
from setuptools import setup, find_packages, Command

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        for root, dirs, files in os.walk("./", topdown=False):
            for name in files:
                if name.endswith((".pyc", ".tgz", ".whl")):
                    print("remove {}".format(os.path.join(root, name)))
                    os.remove(os.path.join(root, name))
            for name in dirs:
                if name.endswith((".egg-info", "build", "dist", "__pycache__", "html")):
                    print("remove {}".format(os.path.join(root, name)))
                    #os.rmdir(os.path.join(root, name))
                    os.system('rm -vrf {}'.format(os.path.join(root, name)))

#Use the README.md file as the pypi description
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

BUILD_ID = os.environ.get('TRAVIS_BUILD_NUMBER', 0)
if BUILD_ID == 0:
    BUILD_ID = os.environ.get('GITHUB_RUN_NUMBER', 0)

setup(
    name='ibmvia_autoconf',
    version='0.3.%s' % BUILD_ID,
    description='YAML based configuration automation for IBM Verify Identity Access',
    author='Lachlan Gleeson',
    author_email='lgleeson@au1.ibm.com',
    license='Apache2.0',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=['requests',
                      'PyYAML',
                      'pyivia',
                      'kubernetes',
                      'docker-compose',
                      'typing'
    ],
    project_urls={
        'Homepage': 'https://github.com/lachlan-ibm/ibmvia_autoconf',
        'Documentation': 'https://lachlan-ibm.github.io/ibmvia_autoconf',
        'Source': 'https://github.com/lachlan-ibm/ibmvia_autoconf',
        'Tracker': 'https://github.com/lachlan-ibm/ibmvia_autoconf/issues'
    },
    zip_safe=False,
    cmdclass={
        'clean': CleanCommand,
    },
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=["ivia", "isva", "isam", "ibm verify", "ibm verify identiy access", 
                    "ibm security access manager", "ibm security verify access"]
)
