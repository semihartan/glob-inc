import os
import subprocess
import argparse
from xml.dom.minidom import *

VS_INSTALL_PATH = None
MSBUILD_VC_PATH =  "\\MSBuild\\Microsoft\\VC\\v170"

NECCESSARY_FILES = ["Microsoft.Cpp.MSVC.Toolset.Common.props", "Microsoft.Cpp.MSVC.Toolset.Win32.props", "Microsoft.Cpp.MSVC.Toolset.x64.props", "Microsoft.Cpp.MSVC.Toolset.ARM.props", "Microsoft.Cpp.MSVC.Toolset.ARM64.props"]

PATCH_TEMPLATES = [ 
"<ItemDefinitionGroup><ClCompile><AdditionalIncludeDirectories>{0}</AdditionalIncludeDirectories></ClCompile></ItemDefinitionGroup>", 
"<ItemDefinitionGroup><Link><AdditionalLibraryDirectories>{0}</AdditionalLibraryDirectories></Link></ItemDefinitionGroup>"]

ROOT_PATH_NAME = 'C:\\3rdparty\\'

SUB_DIRS = ['include\\', 'lib\\x86\\', 'lib\\x64\\', 'lib\\arm\\', 'lib\\arm64' ]

FULL_PATHS = []


# Utility function to create directories if they don't exist.
def create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)

# Utility function to remove a node matching a criteria specified with predicate.
def remove_node(dom: Node, predicate): 
    for child in dom.childNodes:
        if predicate(child):
            dom.removeChild(child)
    for child in dom.childNodes:
        remove_node(child)

# The Python's built-in XML parser parses white-spaces into parse tree. We don't want them because when rebuilding
# XML file, they causes extra whitespace, newlines. 
# This function recursively traverses the DOM, and remove whitespace nodes.
def clean_dom(dom: Node):
    criteria = lambda child : child.nodeName == '#text' and child.nodeValue.startswith(('\n', '\t', ' '))
    remove_node(dom, criteria)

# Remove the ItemDefinitionGroup that we've created.
def remove_item_def_group(dom):
    def criteria(child):
        if child.nodeName == 'ItemDefinitionGroup':
            clcompiles = child.getElementsByTagName('ClCompile')
            for clcompile in clcompiles: 
                aids = clcompile.getElementsByTagName('AdditionalIncludeDirectories')
                for aid in aids:
                    if aid.firstChild.nodeName == '#text' and aid.firstChild.nodeValue == FULL_PATHS[0]:
                        return True
            links = child.getElementsByTagName('Link')
            for link in links: 
                alds = link.getElementsByTagName('AdditionalLibraryDirectories')
                for ald in alds:
                    for i in range(1, len(FULL_PATHS)):
                        if ald.firstChild.nodeName == '#text' and ald.firstChild.nodeValue == FULL_PATHS[i]:
                            return True
            return True
        return False 
    remove_node(dom, criteria)

def get_vs_install_dir():
    completion = subprocess.run('"C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe" -latest -property installationPath', stdout=subprocess.PIPE)
    return completion.stdout.decode()

def check_core(itemDefinitionGroup, type, path):
    childItems = itemDefinitionGroup.getElementsByTagName(type)
    for clCompile in childItems:
        if type == 'ClCompile':
            additionalIncludeDirectories = clCompile.getElementsByTagName('AdditionalIncludeDirectories')
        else:
            additionalIncludeDirectories = clCompile.getElementsByTagName('AdditionalLibraryDirectories')
        for additionalIncludeDirectory in additionalIncludeDirectories:
            if additionalIncludeDirectory.firstChild.nodeValue == path:
                return True
    return False

def check_patch_status():
    global xml_doms
    global check_flags
    xml_doms = [] 
    #              Common, Win32, x64  , ARM  , ARM64
    check_flags = [0,  0, 0, 0, 0]
    check_data = [['ClCompile', 'C:\\3rdparty\\include\\'], ['Link', 'C:\\3rdparty\\lib\\x86\\'], ['Link', 'C:\\3rdparty\\lib\\x64\\'], ['Link', 'C:\\3rdparty\\lib\\arm\\'], ['Link', 'C:\\3rdparty\\lib\\arm64\\']]
    for i, file_name in enumerate(NECCESSARY_FILES):
        file_path = os.path.join(MSBUILD_VC_PATH, file_name)
        with open(file_path, encoding='utf-8') as f:
            xml_string = f.read()
            dom = parseString(xml_string)
            clean_dom(dom)
            xml_doms.append(dom)
            itemDefinitionGroups = dom.getElementsByTagName('ItemDefinitionGroup')
            for itemDefinitionGroup in itemDefinitionGroups:
                for i, cd in enumerate(check_data):
                   if check_core(itemDefinitionGroup, cd[0], cd[1]):
                        check_flags[i] = 1
                        break
    return sum(check_flags) > 0

def patch_files():
    for i, file_name in enumerate(NECCESSARY_FILES): 
        # If toolset_common is patched, skip
        if check_flags[i]:
            continue 

        file_path = os.path.join(MSBUILD_VC_PATH, file_name)
        with open(file_path, mode="r+", encoding='utf-8') as f:
            dom = xml_doms[i]
            project = dom.getElementsByTagName('Project')[0]
            project.appendChild(patch_doms[i])
            xml = dom.toprettyxml(indent='  ').replace('<?xml version="1.0" ?>', "")
            f.write(xml)

def unptach_files():
    for i, file_name in enumerate(NECCESSARY_FILES): 
        # If toolset_common is patched, skip
        if check_flags[i]:
            continue 

        file_path = os.path.join(MSBUILD_VC_PATH, file_name)
        with open(file_path, mode="r+", encoding='utf-8') as f:
            dom = xml_doms[i]
            project = dom.getElementsByTagName('Project')[0]
            remove_item_def_group(project)
            xml = dom.toprettyxml(indent='  ').replace('<?xml version="1.0" ?>', "")
            f.write(xml)

def create_directories():
    sub_dirs = ['']
   
    if not os.path.exists(ROOT_PATH_NAME):
        os.mkdir(ROOT_PATH_NAME)

    create_dir_if_not_exists(FULL_PATHS[0])
    platform = args.platform
    for arch in ['x86', 'arm']:
        path = None
        idx_off = 2 if arch == 'arm' else 0
        if platform.startswith(arch):
            if not platform.endswith('64'):
                path = FULL_PATHS[1 + idx_off] 
                create_dir_if_not_exists(path)
            if not platform.endswith('32'):
                path = FULL_PATHS[2 + idx_off]
                create_dir_if_not_exists(path)      
    
def main():
    global patch_doms
    global args

    VS_INSTALL_PATH = get_vs_install_dir()
    if not VS_INSTALL_PATH or VS_INSTALL_PATH == '':
        print("There is no Visual Studio installation in your system.")
        return
    
    MSBUILD_VC_PATH = os.path.join(VS_INSTALL_PATH, MSBUILD_VC_PATH)
    
    arg_parser = argparse.ArgumentParser(description="glob-inc - A utility script to patch the neccesary MSBuild files to add third party C/C++ libraries to all the C/C++ projects globally.")

    arg_parser.add_argument("--path", type=str, help="The path of the root directory containing include and library directories.", default=ROOT_PATH_NAME)

    arg_parser.add_argument('-c', '--create', help="Create the directories according to the recommended structure if they doesn't exist.", action='store_true', default=False)
    
    arg_parser.add_argument('-p', '--platform', help="The platform(s) for which the patching will be performed.", type=str, default='x86', choices=['x86', 'x86-32', 'x86-64', 'arm', 'arm32', 'arm64'])
    args = arg_parser.parse_args(['-c', 'False', '-p', 'arm64'])

    arg_parser.add_argument('-u', '--unpatch', help="Unpatch the files patched previously.", action='store_true', default=False)
    
    patch_doms = []

    for i, sub_dir in enumerate(SUB_DIRS):
        FULL_PATHS.append(os.path.join(args.path, sub_dir))
        if i == 0:
            patch_doms.append(parseString(PATCH_TEMPLATES[0].format(os.path.join(args.path, SUB_DIRS[0]))).firstChild)
        else:
            patch_doms.append(parseString(PATCH_TEMPLATES[1].format(os.path.join(args.path, sub_dir))).firstChild)

    if args.create:
        create_directories()

    if check_patch_status():
        print("The patch is already done.")
        return
    
    if args.unpatch:
        unptach_files()
    
    patch_files()
    
if __name__ == '__main__':
    main()
