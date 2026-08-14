import maya.cmds as cmds
import os

def validate(filepath):
    """
    Opens filepath in Maya and checks for export issues
    Returns a list of issue strings: empty = no issues
    """
    if not os.path.exists(filepath):
        return ["File does not exist"]

    cmds.file(filepath, open=True, force=True) # open file in maya even with unsaved changes

    issues = []
    issues.extend(check_nonmanifold()) # adds new issues to existing list after each check without nesting
    issues.extend(check_missing_texture())
    issues.extend(check_duplicate_names())
    return issues # list of files that did not pass the filter 

def freeze_transforms():
    """
    Freezes transforms on all objects in file
    """
    cmds.select(all=True) 
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)

def check_nonmanifold():
    """
    Filters files containing mesh with non manifold geometry 
    """
    issues = []
    all_mesh = cmds.ls(t='mesh') # grab all mesh objects in file
    for mesh in all_mesh:
        if cmds.polyInfo(mesh, nonManifoldVertices=True): # check if mesh has weird geomtry
            issues.append("Mesh contains non-manifold geometry")
            break
    return issues

def check_missing_texture():
    """
    Filters files with missing/broken texture references
    """
    issues = []
    all_textures = cmds.ls(t='file') # grab all textures in file
    for texture in all_textures:
        texture_path = cmds.getAttr(f'{texture}.fileTextureName') 
        if not os.path.exists(texture_path): # if the texture path doesn't exist in disk
            issues.append("Mesh is missing texture file")
            break
    return issues
    
def check_duplicate_names():
    """
    Filters files with duplicate names
    """
    issues = []
    all_transforms = cmds.ls(t='transform') # get transform name of all objects in file 
    short_names = [name.split('|')[-1] for name in all_transforms] # short name of every object
    if len(short_names) != len(set(short_names)): # if file has duplicates add to issue list
        issues.append("Mesh contains duplicate names")
    return issues

def export_one(filepath, output_dir):
    """
    Exports one validated file to FBX in output directory
    """
    if not os.path.isdir(output_dir): # output directory check
        cmds.warning("Output directory does not exist. New directory created")
        os.mkdir(output_dir)

    cmds.select(all=True) # select all objects in file

    base_name = os.path.basename(filepath)
    new_name = os.path.splitext(base_name)[0] # get file name and remove extension
    output_path = os.path.join(output_dir, new_name + ".fbx") # create output path

    cmds.file(output_path, exportSelected=True, type="FBX export", force=True) # export to fbx


def batch_export(file_list, output_dir):
    """
    Validates then exports all files within given list to output directory
    """
    failed = []
    if len(file_list) < 1: 
        cmds.warning("File list empty!")
        return failed

    for file in file_list: # if file fails then add to failed list, else export to output dir
        issues = validate(file)
        if issues: # catches known issues
            failed.append((file, ", ".join(issues)))
        else:
            try: # catches other unknown issues
                freeze_transforms()
                export_one(file, output_dir) 
            except Exception as e:
                failed.append((file, str(e))) # add file to failed list if it has issues
    return failed

def print_report(failed):
    """
    Prints a summary of failed exports
    """
    if len(failed) < 1:
        print("All files exported successfully!")
        return

    print(f"{len(failed)} files failed to export:")
    for file, reason in failed:
        print(f"- {file} : {reason}")

    
# run
file_list = [...] # fill with paths
output_dir = "..." # fill with output directory
failed = batch_export(file_list, output_dir)
print_report(failed)