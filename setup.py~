from setuptools import setup, find_packages

setup(
    name="simpleRM",
    version="0.1.0",
    description="Simple Rotation Measure calculations, wrapping around RMExtract",
    author="David Kaplan",
    author_email="kaplan@uwm.edu",
    url="",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "getRM=simpleRM.scripts.getRM:main",
            "getRM_psrfits=simpleRM.scripts.getRM_psrfits:main",
            "getRM_psrchive=simpleRM.scripts.getRM_psrchive:main",
        ],
    },
    install_requires=["astropy", "pyephem", "loguru", "scipy"],
    python_requires=">=3.7",
    package_data={"simpleRM": ["data/*.*"]},
    include_package_data=True,
    zip_safe=False,
)
