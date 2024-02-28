from setuptools import setup, find_packages


setup(
    name="experiment_tracker",
    version="0.1.1",
    author="Tommaso Bendinelli",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "PyYAML",
        "plotly",
        "streamlit",
        "flatten-dict",
        "coloredlogs",
        "hydra-core",
        ],
    package_data={'': ['gui/resources/*.svg']},
    include_package_data=True,

)
