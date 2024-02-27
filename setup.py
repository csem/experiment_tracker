from setuptools import setup, find_packages


setup(
    name="experiment_tracker",
    version="0.0.8",
    author="Tommaso Bendinelli",
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

)
