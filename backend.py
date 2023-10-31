# imports from config.py
from config_data import *

import os,shutil,json,urllib.request,zipfile,io,urllib.parse,glob,sys

def load_config_by_name(file_name):
    print(f"loading config from file: {file_name}...")
    # Load the configuration JSON file
    with open(f"./configs/{file_name}.json", "r") as f:
        config_json = f.read()
    try:
        config = json.loads(config_json)
        print(json.dumps(config, indent=4))
        return config
    except ValueError:
        print('Invalid configuration object')
        exit(1)

def load_config_by_json(config_json):
    try:
        config = json.loads(config_json)
        print(json.dumps(config, indent=4))
        return config
    except ValueError:
        print('Invalid configuration object')
        exit(1)

def delete_build_dir(build_dir_path):
    try:
        # If the directory exists, delete it recursively
        if os.path.exists(build_dir_path):
            shutil.rmtree(build_dir_path)
            print(f'Deleted directory: {build_dir_path}')

        # Create the directory
        os.makedirs(build_dir_path)
        print(f'Created directory: {build_dir_path}')
    except Exception as e:
        print(f'Error: {e}')

def extract_zip(downloads_zip_path, temp_dir_path):
    # Extract the contents to the temporary directory
    print('Extracting repository contents...')
    with zipfile.ZipFile(downloads_zip_path, 'r') as zip_ref:
        extracted_dir = zip_ref.namelist()[0]
        extracted_path = os.path.join(temp_dir_path, extracted_dir)
        zip_ref.extractall(temp_dir_path)
    print('Repository contents extracted successfully.')

    # Move all files to the temp directory
    print('Moving all files to the temp directory...')
    for item in os.listdir(extracted_path):
        item_path = os.path.join(extracted_path, item)
        shutil.move(item_path, temp_dir_path)
    print('All files moved successfully.')
    
    return temp_dir_path

def download_zip(temp_dir_path, tag_ver):
    zip_name = DOWNLOAD_ZIP_NAME.format(tag_ver)
    downloads_zip_path = os.path.join(DOWNLOADS_DIR, zip_name)

    # Check if temp directory already contains files
    if os.path.exists(temp_dir_path) and os.listdir(temp_dir_path):
        print('Temp directory already contains files, skipping download and extraction.')
        return temp_dir_path

    # Check if zip file already exists in downloads directory
    if os.path.exists(downloads_zip_path):
        print('Zip file already exists in downloads directory, skipping download.')
    else:
        # Download the zip file
        os.mkdir(DOWNLOADS_DIR)
        print('Downloading repository from {}...'.format(DOWNLOAD_URL.format(tag_ver)))
        response = urllib.request.urlopen(DOWNLOAD_URL.format(tag_ver))
        with open(downloads_zip_path, 'wb') as f:
            f.write(response.read())
        print('Repository downloaded successfully.')

    # Extract the contents to the temporary directory
    extract_zip(downloads_zip_path, temp_dir_path)

    # Move all files to the temp directory
    print('Moving all files to the temp directory...')
    #for item in os.listdir(temp_dir_path):
    #    item_path = os.path.join(temp_dir_path, item)
    #    #shutil.move(item_path, temp_dir_path)
    #print('All files moved successfully.')

    return temp_dir_path

def copy_temp_to_build(temp_dir_path, build_dir_path, name_index):
    # Find the directory with index.html
    while not os.path.exists(os.path.join(temp_dir_path, name_index)):
        temp_dir_path = os.path.join(temp_dir_path, os.listdir(temp_dir_path)[0])
        
    # Copy files and directories to build directory
    for item in os.listdir(temp_dir_path):
        item_path = os.path.join(temp_dir_path, item)
        if os.path.isfile(item_path):
            shutil.copy(item_path, build_dir_path)
        elif os.path.isdir(item_path):
            shutil.copytree(item_path, os.path.join(build_dir_path, item))
        else:
            print(f"Unsupported file type: {item_path}")

def validate_button_class(dir_path,name):
    path = BRANDS_CSS_FILE.format(dir_path)
    with open(path, 'r') as f:
        css = f.read()

    button_class = BUTTON_CLASS_NAME.format(name)
    
    return button_class in css

def validate_button_image(dir_path,name):
    path = IMAGES_ICONS.format(dir_path,name)
    return os.path.exists(path)

def generate_buttons_html(config,dir_path,create_index,config_name):
    # Extract the button details from the LINKS object list
    buttons = config[CONFIG_LINKS]
    button_details = [(button.get(CONFIG_LINKS_KEY_TYPE, BUTTON_DETAILS_DEF_TYPE), button.get(CONFIG_LINKS_KEY_NAME, BUTTON_DETAILS_DEF_NAME), button.get(CONFIG_LINKS_KEY_ICON, BUTTON_DETAILS_DEF_ICON), button.get(CONFIG_LINKS_KEY_URL, BUTTON_DETAILS_DEF_URL)) for button in buttons]

    # Generate new HTML code for the buttons
    button_html = ''
    for button_type, button_name, button_icon, button_link in button_details:
        if create_index:
            if config_name != "index":
                button_link = "/{}{}".format(config_name, button_link)
            else:
                button_link = "{}".format(button_link)
        
        if not config[CONFIG_BASE_SHORT_URL] is None:
            button_link = config[CONFIG_BASE_SHORT_URL] + button_link

        if not validate_button_class(dir_path,button_type):
            button_type = BUTTON_DETAILS_DEF_TYPE

        if not validate_button_image(dir_path,button_icon):
            button_icon = BUTTON_DETAILS_DEF_ICON

        print(f"\nbutton: {button_type}\nurl: {button_link}\nicon: {button_icon}\nname: {button_name}")
        button_html += '\t\t\t\t<!-- %s -->\n' % button_name
        button_html += '\t\t\t\t<a class="button button-%s" href="%s" target="_blank" rel="noopener" role="button"><img class="icon" src="images/icons/%s.svg" alt="">%s</a><br>\n' % (button_type, button_link, button_icon, button_name)

    return button_html

def generate_index_html(config, dir_path, create_index, config_name, name_index):
    # Read HTML file
    with open(TEMPLATE_HTML, 'r') as f:
        html = f.read()

    # Replace variables in HTML
    replaced_html = html \
        .replace('{{META_ICON_URL}}', config["META"][CONFIG_META_ICON_URL]) \
        .replace('{{META_TITLE}}', config["META"][CONFIG_META_TITLE]) \
        .replace('{{META_AUTHOR}}', config["META"][CONFIG_META_AUTHOR]) \
        .replace('{{META_DESCRIPTION}}', config["META"][CONFIG_META_DESCRIPTION]) \
        .replace('{{META_THEME}}', config["META"][CONFIG_META_THEME]) \
        .replace('{{BIO_ICON_URL}}', config["BIO"][CONFIG_BIO_ICON_URL]) \
        .replace('{{BIO_TITLE}}', config["BIO"][CONFIG_BIO_ICON_TITLE]) \
        .replace('{{BIO_DESCRIPTION}}', config["BIO"][CONFIG_BIO_DESCRIPTION]) \
        .replace('{{BIO_FOOTER}}', config["BIO"][CONFIG_BIO_FOOTER]) \
        .replace('{{BIO_BUTTONS}}', generate_buttons_html(config,dir_path,create_index,config_name))

    # Write replaced HTML back to file
    with open(os.path.join(dir_path, name_index), 'w') as f:
        f.write(replaced_html)

    print('\nHTML file updated!')

def delete_unnecessary_files(dir_path):
    print('Deleting unnecessary files and directories...')
    for file_path in FILES_TO_DELETE:
        full_path = os.path.join(dir_path, file_path)
        try:
            if os.path.isdir(full_path):
                if file_path.startswith("littlelink-"):
                    shutil.rmtree(full_path)
                    print('Removed directory: {}'.format(full_path))
            elif os.path.exists(full_path):
                os.remove(full_path)
                print('Removed file: {}'.format(full_path))
        except Exception as e:
            print('Error deleting {}: {}'.format(full_path, e))
    
    # Add code to delete folders starting with "littlelink-"
    for item in os.listdir(dir_path):
        full_path = os.path.join(dir_path, item)
        try:
            if os.path.isdir(full_path) and item.startswith("littlelink-"):
                shutil.rmtree(full_path)
                print('Removed directory: {}'.format(full_path))
        except Exception as e:
            print('Error deleting {}: {}'.format(full_path, e))
    
    print('Deletion complete!')

def generate_redirects_file(config, dir_path):
    redirects_enabled = config.get(REDIRECTS, {}).get(CONFIG_REDIRECTS_ENABLED, False)
    if redirects_enabled:
        redirects = config.get(REDIRECTS, {}).get(CONFIG_REDIRECTS_LINKS, [])
        if not redirects:
            print('Error: No links in _REDIRECTS configuration')
            return
        redirects_file_path = os.path.join(dir_path, REDIRECTS_FILE)
        with open(redirects_file_path, 'w') as f:
            for redirect in redirects:
                f.write(f"{redirect[CONFIG_REDIRECTS_KEY_NAME]} {redirect[CONFIG_REDIRECTS_KEY_URL]} {redirect[CONFIG_REDIRECTS_KEY_CODE]}\n")

def create_zip(temp_dir, build_dir, zip_name="links"):
    # Get the name of the directory
    dir_name = os.path.basename(temp_dir)

    # Create the zip file name
    if zip_name is None:
        zip_name = f"{dir_name}.zip"
    else:
        zip_name = f"{zip_name}.zip"

    # Create the zip file with the given name
    zip_path = os.path.join(build_dir, zip_name)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Iterate over all files and directories in the directory
        for root, dirs, files in os.walk(temp_dir):
            # Add all files to the zip file
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, temp_dir))
            # Add all directories to the zip file (empty directories will be skipped)
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                zipf.write(dir_path, os.path.relpath(dir_path, temp_dir))

    print(f"Zip file created at {zip_path}")
    return zip_path
