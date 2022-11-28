import io
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, "README.rst"), "rt", encoding="utf8") as f:
    readme = f.read()

about = {}
with io.open(
    os.path.join(here, "tutorminio", "__about__.py"), "rt", encoding="utf-8"
) as f:
    exec(f.read(), about)


setup(
    name="tutor-minio",
    version=about["__version__"],
    url="https://docs.tutor.overhang.io/",
    project_urls={
        "Documentation": "https://docs.tutor.overhang.io/",
        "Code": "https://github.com/overhangio/tutor-minio",
        "Issue tracker": "https://github.com/overhangio/tutor-minio/issues",
        "Community": "https://discuss.overhang.io",
    },
    license="AGPLv3",
    author="Overhang.io",
    author_email="contact@overhang.io",
    description="A Tutor plugin for object storage in MinIO",
    long_description=readme,
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=["tutor>=15.0.0,<16.0.0"],
    entry_points={"tutor.plugin.v1": ["minio = tutorminio.plugin"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
