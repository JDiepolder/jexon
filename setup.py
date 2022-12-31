"""Setup jexon
"""

import subprocess
import os
import re
import json
import setuptools

_VERSION_FILE_PATH = os.path.join('jexon', 'VERSION')
_REQUIREMENTS_FILE_PATH = os.path.join('jexon', 'REQUIREMENTS')

if not os.path.isfile(_VERSION_FILE_PATH):
    jexon_version = (
        subprocess.run(
            ["git", "describe", "--tags"],
            stdout=subprocess.PIPE,
            check=True,
        )
        .stdout
        .decode('utf-8')
        .strip()
    )

    print(jexon_version)

    assert re.fullmatch(r"\d+\.\d+\.\d+", jexon_version), \
        f"No valid version found: {jexon_version}!"

    with open(_VERSION_FILE_PATH, 'w', encoding="utf-8") as f:
        f.write(jexon_version)
else:
    with open(_VERSION_FILE_PATH, 'r', encoding="utf-8") as f:
        jexon_version = f.read().strip()

if not os.path.isfile(_REQUIREMENTS_FILE_PATH):
    with open("requirements.txt", "r", encoding="utf-8") as f:
        requires = f.read().split()

    with open(_REQUIREMENTS_FILE_PATH, 'w', encoding="utf-8") as f:
        json.dump(requires, f)
else:
    with open(_REQUIREMENTS_FILE_PATH, 'r', encoding="utf-8") as f:
        requires = json.load(f)

setuptools.setup(
    name="jexon",
    version=jexon_version,
    author="Johannes Diepolder",
    author_email="Johannes.Diepolder@tum.de",
    description="Executable json",
    long_description="Executable json",
    url="https://github.com/JDiepolder/jexon",
    packages=setuptools.find_packages(exclude=["tests*"]),
    package_data={"jexon": ["VERSION", "REQUIREMENTS"]},
    include_package_data=True,
    install_requires=requires,
)
