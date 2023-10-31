# imports from config.py
from config_data import *
from backend import *
import argparse

def process_configs(create_index_build,zip_files):
    for file_name in os.listdir('./configs'):
        if file_name.endswith('.json'):
            json_file = os.path.splitext(file_name)[0]
            if create_index_build or json_file != "index":
                print(f'config: {json_file}')
                main(json_file, create_index_build,zip_files)

def main(config_name,create_index_build, zip_files):
    
    # Load configuration
    config = load_config_by_name(config_name)
    
    # Check tag version for download url
    ver_tag = config.get(DOWNLOAD_TAG_VER, DOWNLOAD_TAG_DEF_VER)
    print(f'tag version to download: {ver_tag}')

    _create_index_build = create_index_build
    print(f"create index: {_create_index_build}")

    # Define paths
    if _create_index_build:
        html_index_name = INDEX_NAME.format(config_name)
    else:
        html_index_name = INDEX_NAME.format("index")
    
    if _create_index_build:
        build_dir_path = os.path.join(os.getcwd(), BUILD_DIR.format("index"))
    else:
        build_dir_path = os.path.join(os.getcwd(), BUILD_DIR.format(config_name))
        
    html_path = os.path.join(build_dir_path, html_index_name)
    
    temp_dir_path = os.path.join(os.getcwd(), TEMP_DIR.format(config_name))

    print(f'\nbuild_dir_path: {build_dir_path}\nhtml_path: {html_path}\ntemp: {temp_dir_path}')

    # Delete old build directory and create new one
    if not _create_index_build:
        # Only delete build_dir_path if it doesn't end with 'index'
        if not build_dir_path.endswith('/index'):
            delete_build_dir(build_dir_path)
    else:
        os.makedirs(build_dir_path, exist_ok=True)

    # Download LittleLink repository
    _tempDIR = download_zip(temp_dir_path,ver_tag)
    
    # Delete unnecessary files and directories
    delete_unnecessary_files(_tempDIR)

    # Generate HTML file
    generate_index_html(config,_tempDIR,create_index_build,config_name,html_index_name)
    
    # Generate a _redirect file
    if not _create_index_build:
        generate_redirects_file(config,_tempDIR)
    elif config_name == "index":
        generate_redirects_file(config,_tempDIR)

    # Copy temp to the build dir.
    if not _create_index_build:
        copy_temp_to_build(temp_dir_path, build_dir_path, html_index_name)
        print(f"copied {temp_dir_path} to {build_dir_path}")
    elif _create_index_build and config_name == "index":
        copy_temp_to_build(temp_dir_path, build_dir_path, html_index_name)
        print(f"copied {temp_dir_path} to {build_dir_path}")
    else:
        old_file_path = os.path.join(temp_dir_path, html_index_name)
        new_file_path = os.path.join(build_dir_path, f"{config_name}.html")
        shutil.copy(old_file_path, new_file_path)
        print(f"copied {old_file_path} to {new_file_path}")

    # Generate a zip file file
    if not _create_index_build:
        if zip_files:
            create_zip(_tempDIR, build_dir_path, config_name)
        else:
            print("zip files not enabled, use --zip")


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true', help='process all config files')
    parser.add_argument('--clear', action='store_true', help='clear temp and build')
    parser.add_argument('--single', action='store_true', help='creates a single links page for all generated files.')
    parser.add_argument('--name', help='process a single file')
    parser.add_argument('--zip', action='store_true', help='zip the build/XXX dir')
    
    args = parser.parse_args()

    if args.clear:
        delete_build_dir("./build")
        delete_build_dir("./temp")

    if args.all:
        process_configs(args.single,args.zip)
        if args.zip:
            create_zip("./build/index","./build", "index") 
    elif args.name:
        main(args.name, False,args.zip)
    else:
        print('Error: No arguments specified. Use --all or --name <file_name>.')