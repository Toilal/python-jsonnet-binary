import os

from setuptools import Extension, setup
from setuptools.command.build_clib import build_clib


class BuildCLib(build_clib):
    """Builds jsonnet library"""

    cflags = {
        "msvc": ["/EHsc", "/Ox"],
        "unix": [
            "-g",
            "-O3",
            "-Wall",
            "-Wextra",
            "-Woverloaded-virtual",
            "-pedantic",
            "-std=c++0x",
            "-fPIC",
        ],
    }

    def _buildstdlib(self):
        """Builds the byte-array for stdlib."""

        with open("jsonnet/stdlib/std.jsonnet", "rb") as f:
            stdlib = bytearray(f.read())
        with open("jsonnet/core/std.jsonnet.h", "w") as f:
            for byte in stdlib:
                f.write("%d," % byte)
            f.write("0")

    def _patchcflags(self, libraries):
        """Add in cflags."""

        compiler = self.compiler.compiler_type
        args = self.cflags[compiler]
        for lib in libraries:
            lib[1]["cflags"] = args

    def build_libraries(self, libraries):
        self._patchcflags(libraries)
        self._buildstdlib()
        super(BuildCLib, self).build_libraries(libraries)


DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(DIR, 'README.md'), encoding='utf-8') as f:
    readme = f.read()


def get_libjsonnet_version():
    """
    Parses the version out of libjsonnet.h. This is a copy/paste from official setup.py.
    """
    with open(os.path.join(DIR, 'jsonnet/include/libjsonnet.h')) as f:
        for line in f:
            if '#define' in line and 'LIB_JSONNET_VERSION' in line:
                v_code = line.partition('LIB_JSONNET_VERSION')[2].strip('\n "')
                if v_code[0] == "v":
                    v_code = v_code[1:]
                return v_code


post_release_segment = ""  # ".post0"
"""
The post release segment of jsonnet-binary, appended after version of jsonnet.

It should be defined to release a new version of jsonnet-binary packages, but jsonnet version is still the same.

`See PEP 440 Post Releases <https://www.python.org/dev/peps/pep-0440/#post-releases>`_.
"""

setup(
    name="jsonnet-binary",
    url="https://github.com/Toilal/python-jsonnet-binary",
    description="An UNOFFICIAL Python interface to Jsonnet, "
                "available as whl packages for Mac, Linux and Windows.",
    long_description=readme,
    long_description_content_type='text/markdown',
    author="Matt Covalt",
    author_email="mcovalt@mailbox.org",
    maintainer="Rémi Alvergnat",
    maintainer_email="toilal.dev@gmail.com",
    version=get_libjsonnet_version() + post_release_segment,
    ext_modules=[
        Extension(
            "_jsonnet",
            sources=["jsonnet/python/_jsonnet.c"],
            libraries=["jsonnet"],
            include_dirs=[
                "jsonnet/include",
                "jsonnet/third_party/json",
                "jsonnet/third_party/md5",
            ],
            language="c++",
        )
    ],
    libraries=[
        [
            "jsonnet",
            {
                "sources": [
                    "jsonnet/core/desugarer.cpp",
                    "jsonnet/core/formatter.cpp",
                    "jsonnet/core/libjsonnet.cpp",
                    "jsonnet/core/lexer.cpp",
                    "jsonnet/core/parser.cpp",
                    "jsonnet/core/pass.cpp",
                    "jsonnet/core/static_analysis.cpp",
                    "jsonnet/core/string_utils.cpp",
                    "jsonnet/core/vm.cpp",
                    "jsonnet/third_party/md5/md5.cpp",
                ],
                "include_dirs": [
                    "jsonnet/include",
                    "jsonnet/third_party/json",
                    "jsonnet/third_party/md5",
                ],
            },
        ]
    ],
    cmdclass={"build_clib": BuildCLib},
)
