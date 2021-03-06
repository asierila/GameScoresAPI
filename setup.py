from setuptools import find_packages, setup

# from course example https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/setup.py  # noqa: E501
setup(
    name="gamescoresapi",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flask-restful",
        "flask-sqlalchemy",
        "SQLAlchemy",
    ]
)
