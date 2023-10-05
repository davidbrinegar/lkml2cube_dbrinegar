import pprint
import typer
import yaml
import os
import json

from lkml2cube.parser.explores import parse_explores, generate_cube_joins
from lkml2cube.parser.loader import file_loader, write_files
from lkml2cube.parser.views import parse_view
from typing_extensions import Annotated

app = typer.Typer()

def find_explores_including_view(lkml_root, view_name):
    explores = []
    for root, dirs, files in os.walk(lkml_root):
        for file in files:
            if file.endswith(".lookml"):  # Adjust the extension as needed
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    try:
                        content = json.load(f)  # Adjust as needed for the file format
                        if view_name in str(content):  # Adjust this check as needed
                            explores.append(content)
                    except Exception as e:
                        print(f"Could not load or parse file {file_path}: {e}")
    return explores

@app.callback()
def callback():
    """
    lkml2cube is a tool to convert LookML models into Cube data models.
    """
    # typer.echo(("lkml2cube is a tool to convert LookML models into Cube data models.\n"
    #             "Use lkml2cube --help to see usage."))
    pass

@app.command()
def cubes(
        file_path: Annotated[str, typer.Argument(help="The path for the file to read")],
        parseonly: Annotated[bool, typer.Option(help=("When present it will only show the python"
                                                      " dict read from the lookml file"))] = False,
                                                      
        outputdir: Annotated[str, typer.Option(help="The path for the output files to be generated")] = '.',
        printonly: Annotated[bool, typer.Option(help="Print to stdout the parsed files")] = False,
        lkml_root: Annotated[str, typer.Option(help="The LookML source root directory")] = '.',
    ):
    """
    Generate cubes-only given a LookML file that contains LookML Views.
    """
    
    lookml_model = file_loader(file_path)
    view_name = "your_view_name"  # You need to extract or know the view name in advance
    explores = find_explores_including_view(lkml_root, view_name)
    if 'explores' not in lookml_model:
        lookml_model['explores'] = []
    lookml_model['explores'].extend(explores)

    if parseonly:
        typer.echo(pprint.pformat(lookml_model))
        return
    
    cube_def = parse_view(lookml_model)
    cube_def = generate_cube_joins(cube_def, lookml_model)
    
    if printonly:
        typer.echo(yaml.dump(cube_def))
        return
    
    write_files(cube_def, outputdir=outputdir)
    


@app.command()
def views(
        file_path: Annotated[str, typer.Argument(help="The path for the explore to read")],
        parseonly: Annotated[bool, typer.Option(help=("When present it will only show the python"
                                                      " dict read from the lookml file"))] = False,
        outputdir: Annotated[str, typer.Option(help="The path for the output files to be generated")] = '.',
        printonly: Annotated[bool, typer.Option(help="Print to stdout the parsed files")] = False,
    ):
    """
    Generate cubes-only given a LookML file that contains LookML Views.
    """
    
    lookml_model = file_loader(file_path)
    if parseonly:
        typer.echo(pprint.pformat(lookml_model))
        return
    
    cube_def = parse_explores(lookml_model)

    if printonly:
        typer.echo(yaml.dump(cube_def))
        return
    
    write_files(cube_def, outputdir=outputdir)

if __name__ == "__main__":
    app()

