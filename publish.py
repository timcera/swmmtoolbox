"""Publish package to PyPI."""

import shlex
import shutil
import subprocess

PKG_NAME = "swmmtoolbox"

with open("VERSION", encoding="ascii") as version_file:
    version = version_file.readline().strip()

shutil.rmtree("build", ignore_errors=True)

subprocess.run(shlex.split("pyclean ."), check=True)

subprocess.run(shlex.split("python3 -m build --sdist"), check=True)
subprocess.run(shlex.split("python3 -m build --wheel"), check=True)
sdist = f"dist/{PKG_NAME}-{version}.tar.gz"
wheel = f"dist/{PKG_NAME}-{version}*.whl"

for file in [sdist, wheel]:
    subprocess.run(
        shlex.split(f"twine check {file}"),
        check=True,
    )
    subprocess.run(
        shlex.split(f"twine upload --skip-existing {file}"),
        check=True,
    )

shutil.rmtree("build", ignore_errors=True)
