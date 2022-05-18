from setuptools import setup, find_packages


setup(
    name="csem_exptrack",
    version="0.0.4",
    author="CSEM",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "PyYAML",
        "plotly",
        "streamlit",
        "flatten-dict",
        "coloredlogs"],
    package_data={'': ['gui/resources/*.svg']},
    include_package_data=True,
    # entry_points={
    #     "console_scripts": [
    #         "clean_folder=CSEM_ExperimentTracker.load_files:delete_empty_folder",
    #         "save_df = CSEM_ExperimentTracker.load_files:save_df",
    #     ]
    # },
)
