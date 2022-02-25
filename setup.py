from setuptools import setup, find_packages

setup(
    name="read_Timer",
    version="0.1.0",
    description="Read PSRCHIVE Timer Headers",
    author="David Kaplan",
    author_email="kaplan@uwm.edu",
    url="",
    packages=find_packages(),
    install_requires=["astropy", "loguru"],
    python_requires=">=3.7",
    package_data={"read_Timer": ["data/*.*"]},
    include_package_data=True,
    zip_safe=False,
)
