from setuptools import setup, find_packages
from pathlib import Path

ROOT = Path(__file__).parent
README = (ROOT / "README.md").read_text(encoding="utf-8")

setup(
    name="agrs",
    version="0.1.0",
    description="AGRS: Agricultural Remote Sensing Library",
    long_description=README,
    long_description_content_type="text/markdown",
    author="AGRS Developers",
    url="https://github.com/abdelghanibelgaid/agrs",
    license="MIT",
    packages=find_packages(exclude=("tests", "examples")),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "numpy",
        "pandas",
        "geopandas",
        "shapely",
        "rasterio",
        "pystac-client",
        "planetary-computer",
        "xarray",
        "tqdm",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords=[
        "agriculture",
        "remote-sensing",
        "geospatial",
        "feature-extraction",
    ],
)
