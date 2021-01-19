from setuptools import setup, find_packages


setup(
    name="csem_experimenttracker",
    version="0.0.1",
    author="CSEM",
    packages=find_packages("../csem_experimenttracker"),
    package_dir={"": "../csem_experimenttracker"},
    entry_points={
        "console_scripts": [
            "clean_folders = load_files:delete_empty_folder",
        ],
    },
)
