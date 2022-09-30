from setuptools import setup, find_packages

setup(
    name="slider",
    version="0.1",
    py_modules=["slider"],
    include_package_data=False,
    packages=["slider", "slider.data"],
    package_dir={"slider": "slider", "slider.data": "slider/data"},
    # TODO: use ** for OpenSLO glob; https://github.com/pypa/setuptools/pull/3309
    package_data={"slider.data": ["*.jsonnet", "OpenSLO/*/*/*.json", "OpenSLO/*/*/*/*.json", "grafonnet/*.libsonnet"]},
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        slider=slider:cli
    """,
)
