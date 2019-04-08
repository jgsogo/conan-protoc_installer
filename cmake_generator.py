
import textwrap
from conans.client.generators import registered_generators

def _protoc_macro(deps_build_info):
    deps = {k: v for k,v in deps_build_info.dependencies}
    if "protoc_installer" in deps:
        cpp_info = deps["protoc_installer"]
        paths = ";".join(cpp_info.bin_paths)
        
        content = textwrap.dedent("""
            macro(protoc_macro)
                message(">>>> This is the macro in the ProtocGenerator")
                message("Path to protoc: {}")
            endmacro()
        """.format(paths))
        return content
    return ""


def _generator_cmake():
    _generator = registered_generators["cmake"]
    class ProtocCMakeGenerator(_generator):
        @property
        def content(self):            
            content = super(ProtocCMakeGenerator, self).content
            content += _protoc_macro(self.deps_build_info)
            return content

    registered_generators.add("cmake", ProtocCMakeGenerator, custom=True)


def _generator_cmake_find_package():
    _generator = registered_generators["cmake_find_package"]
    class ProtocCMakeGenerator(_generator):
        @property
        def content(self):            
            content = super(ProtocCMakeGenerator, self).content
            
            # I can inject the macro in the `Findprotoc_install.cmake` file
            find_protoc = content.pop("Findprotoc_installer.cmake")
            find_protoc += _protoc_macro(self.deps_build_info)
            content["Findprotoc_installer.cmake"] = find_protoc
            
            # ...but also in the `Findprotobuf.cmake` one
            find_protobuf = content.pop("Findprotobuf.cmake", None)
            if find_protobuf:
                find_protobuf += _protoc_macro(self.deps_build_info)
            content["Findprotobuf.cmake"] = find_protobuf

            return content

    registered_generators.add("cmake_find_package", ProtocCMakeGenerator, custom=True)


_generator_cmake()
_generator_cmake_find_package()
