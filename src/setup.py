from setuptools import setup

setup(
    name="slider",
    version="0.1",
    py_modules=["slider"],
    include_package_data=True,
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        slider=slider:cli
    """,
)