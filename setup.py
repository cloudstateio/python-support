"""
Copyright 2020 Lightbend Inc.
Licensed under the Apache License, Version 2.0.
"""
import os
import pathlib

from setuptools import find_packages, setup

# Load version in cloudstate package.
from setuptools.command.build_py import build_py

exec(open("cloudstate/version.py").read())

PROTOBUF_VERSION = "master"

version = __version__  # noqa
name = "cloudstate"

print(f"package name: {name}, version: {version}", flush=True)

proto_lib_roots = ["protobuf/lib"]
proto_roots = ["."]


class FetchBuildProtosCommand(build_py):
    """fetch libs and install the protocol buffer generated sources."""

    def run(self):
        os.system(f"scripts/fetch-cloudstate-pb.sh {PROTOBUF_VERSION}")

        for proto_root in proto_roots + proto_lib_roots:
            for root, subdirs, files in os.walk(proto_root):
                for file in [f for f in files if f.endswith(".proto")]:
                    file_path = pathlib.Path(root) / file
                    destination = "."
                    print(f"compiling {file_path} to {destination}")
                    command = f"python -m grpc_tools.protoc {' '.join([' -I ' + i for i in proto_roots + proto_lib_roots])} --python_out={destination} --grpc_python_out={destination} {file_path}"  # noqa
                    os.system(command)

        return super().run()


packages = find_packages(exclude=[])

print(f"packages: {packages}")
setup(
    name=name,
    version=version,
    url="https://github.com/cloudstateio/python-support",
    license="Apache 2.0",
    description="Cloudstate Python Support Library",
    packages=packages,
    package_data={
        "": ["*.proto"],
    },
    long_description=open("Description.md", "r").read(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    scripts=["scripts/fetch-cloudstate-pb.sh"],
    install_requires=[
        "attrs>=19.3.0",
        "google-api>=0.1.12",
        "googleapis-common-protos >= 1.51.0",
        "grpcio>=1.31.0",
        "grpcio-tools>=1.31.0",
        "protobuf>=3.11.3",
        "pytest>=5.4.2",
        "six>=1.14.0",
        "grpcio-reflection>=1.31.0",
        "docker",
    ],
    cmdclass={
        "build_py": FetchBuildProtosCommand,
    },
)
