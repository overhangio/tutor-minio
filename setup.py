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
    url="https://docs.tutor.edly.io/",
    project_urls={
        "Documentation": "https://docs.tutor.edly.io/",
        "Code": "https://github.com/overhangio/tutor-minio",
        "Issue tracker": "https://github.com/overhangio/tutor-minio/issues",
        "Community": "https://discuss.openedx.org",
    },
    license="AGPLv3",
    author="Edly",
    author_email="hello@edly.io",
    maintainer="Edly",
    maintainer_email="faraz.maqsood@arbisoft.com",
    description="A Tutor plugin for object storage in MinIO",
    long_description=readme,
    long_description_content_type="text/x-rst",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=["tutor>=19.0.0,<20.0.0"],
    extras_require={"dev": "tutor[dev]>=19.0.0,<20.0.0"},
    entry_points={"tutor.plugin.v1": ["minio = tutorminio.plugin"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
