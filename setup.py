from setuptools import setup
import os
# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
setup(
    name = 'Otpadder',
    version = "0.0.1",
    author = "Joey Stevens",
    license = read("LICENSE"),
    keywords = "otp one time pad vigenere cipher",
    description='OTP encrypt/decrypt with full ASCII and UTF support',
    long_description=read('README'),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    packages = ["otp"],
)
