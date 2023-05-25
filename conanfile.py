import os

from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import copy, rmdir, patch
from conans import ConanFile


class TarsConan(ConanFile):
    name = "tars"
    version = "3.0.13"
    description = "C++ language framework rpc source code implementation"
    license = "BDS-3"
    homepage = "https://github.com/TarsCloud/TarsCpp"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/*.patch"
    scm = {
        "type": "git",
        "url": "https://github.com/TarsCloud/TarsCpp.git",
        "submodule": "recursive",
        "revision": "v{}".format(version)
    }

    def source(self):
        patch(self, patch_file=os.path.join(self.source_folder, "patches/remove-gtest.patch"))
        if self.settings.os == 'Windows':
            patch(self, patch_file=os.path.join(self.source_folder, "patches/windows-libcurl-parallel-build.patch"))
        patch(self, patch_file=os.path.join(self.source_folder, "patches/change-protocol-install-destination.patch"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TARS_MYSQL"] = False
        tc.variables["TARS_HTTP2"] = False
        tc.variables["TARS_SSL"] = False
        tc.variables["TARS_PROTOBUF"] = False
        tc.variables["ONLY_LIB"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        variables = {}
        if self.settings.os == 'Windows':
            variables["CMAKE_CXX_FLAGS"] = "/MDd" if self.settings.build_type == 'Debug' else "/MD"
        cmake.configure(variables=variables)
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "makefile"))
        rmdir(self, os.path.join(self.package_folder, "tools"))
        rmdir(self, os.path.join(self.package_folder, "script"))
        rmdir(self, os.path.join(self.package_folder, "thirdparty"))
