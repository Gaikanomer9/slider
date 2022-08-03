from setuptools import setup

setup(
    name="slidergen",
    version="0.1",
    py_modules=["slider-gen"],
    include_package_data=True,
    install_requires=["click"],
    entry_points="""
        [console_scripts]
        slidergen=slidergen:cli
    """,
)