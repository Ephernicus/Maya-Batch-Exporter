import maya.cmds as cmds
import os

def validate(filepath):
    """
    Opens filepath in Maya and checks for export issues
    Returns a list of issue strings: empty = no issues
    """
    issues = []
    issues.extend(check_nonmanifold(filepath)) # adds new issues to existing list after each check without nesting
    issues.extend(check_missing_texture(filepath))
    issues.extend(check_duplicate_names(filepath))
    return issues # list of files that did not pass the filter 

def check_nonmanifold(filepath):
    """
    Filters files containing mesh with non manifold geometry 
    """
    issues = []
    cmds.file(filepath, open=True)
    all_mesh = cmds.ls(t='mesh') # grab all mesh objects in file
    for mesh in all_mesh:
        if not cmds.polyInfo(mesh, nonManifoldVertices=True): # check if mesh has weird geomtry
            cmds.warning("Mesh contains non-manifold geometry")
            issues.append(filepath)
            break
    return issues

def check_missing_texture(filepath):
    """
    Filters files with missing/broken texture references
    """
    issues = []
    cmds.file(filepath, open=True)
    all_textures = cmds.ls(t='file') # grab all textures in file
    for texture in all_textures:
        texture_path = cmds.getAttr(texture, 'fileNode.fileTextureName') 
        if not os.path.exists(texture_path): # if the texture path doesn't exist in disk
            cmds.warning("Mesh is missing texture file")
            issues.append(filepath)
            break
    return issues
    
def check_duplicate_names(filepath):
    """
    Filters files with duplicate names
    """
    issues = []
    cmds.file(filepath, open=True)
    all_transforms = cmds.ls(t='transform') # get transform name of all objects in file 
    for name in all_transforms: # operation to get just the short names
        short_names = all_transforms.split('|')
        short_name = short_names[-1] 

    return issues


def export_one(filepath, output_dir):
    """
    Exports one validated file to FBX in output directory

    Should raise/let exceptions propagate — the caller handles catching.
    """
    pass


def batch_export(file_list, output_dir):
    """
    Runs validate_before_export + export_one across every file in file_list.
    One bad file must not stop the rest.

    Needs to track:
      - succeeded: list of filepaths that exported cleanly
      - failed: list of (filepath, reason) tuples

    Returns (succeeded, failed)
    """
    pass


def print_report(succeeded, failed):
    """
    Prints a summary of export result 
    """
    pass


# --- run it ---
file_list = [...]       # fill with real paths, or leave as a placeholder for now
output_dir = "..."
succeeded, failed = batch_export(file_list, output_dir)
print_report(succeeded, failed)