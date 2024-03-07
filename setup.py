from setuptools import setup, find_packages

setup(
    name="indycarpy",
    version="0.2.0",
    author="Toni Cabrera",
    author_email="tonicabrera@bymat.io",
    description="A Python package to scrape Indycar session data",
    url="https://github.com/TMCabrera/indycarpy",
    packages=find_packages(),
    keywords=["Indycar", "scraper", "motorsport"],
    install_requires=["pandas", "requests", "tqdm", "numpy"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
