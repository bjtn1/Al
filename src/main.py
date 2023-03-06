"""
@author: Brandon Jose Tenorio Noguera
"""
#!/usr/bin/env python3

import argparse
import os
import shutil
import hashlib
from collections import defaultdict

byte_chunk = 1024


def is_hidden_file(file):
    """Returns true if `file` starts with `.`"""
    return file.startswith(".")


def print_table_as_tree(source_table, path):
    source_table = {k: source_table[k] for k in sorted(source_table)}
    source_table = {k: sorted(v) for k, v in source_table.items()}

    print(path)
    print("└── organized-files")

    directory_names = list(source_table.keys())
    
    for directory_name, files in source_table.items():
        if directory_names[-1] == directory_name:
            print(f"    └── {directory_name}")
        else:
            print(f"    ├── {directory_name}")
        for file in files:
            if len(files) == 1:
                print(f"    │   └── {file}")
            elif file == files[-1] and directory_names[-1] == directory_name:
                print(f"        └── {file}")
            elif file == files[-1]:
                print(f"    │   └── {file}")
            elif directory_names[-1] == directory_name:
                print(f"        ├── {file}")
            else:   
                print(f"    │   ├── {file}")
        
        if directory_names[-1] != directory_name:
            print(f"    │")



def get_hash(file_object, iteration):
    """Returns the hash value of the given file object"""
    if iteration == 0:
        file_contents = file_object.read(byte_chunk)
        return hashlib.sha256(file_contents).hexdigest()
    elif iteration == 1:
        file_contents = file_object.read()
        return hashlib.sha256(file_contents).hexdigest()
    else:
        raise Exception("Error encountered in get_hash()")


def add_unique_file_to_table(file, destination_table):
    """Adds given file to the `organized_files` hash table under the appropriate key"""
    _, file_extension = os.path.splitext(file)
    file_extension = file_extension[1:] + "-files" if file_extension else "no-extension-files"  # if file has no extension, assign it the "no-extension" label, otherwise remove the dot
    destination_table[file_extension].append(file)


def rehash_and_add_to_table(list_of_files, destination_table, iteration):
    """Calculates the sha256 of the first 1024 bytes of every files in `list_of_files` and adds them to destination table"""
    for file in list_of_files:
        try:
            with open(file, 'rb') as file_object:
                current_hash = get_hash(file_object, iteration)
        except OSError:
            raise Exception("Unable to read current file")
        destination_table[current_hash].append(file)


def find_duplicate_files(source_table, destination_table, iteration=0):
    potentially_duplicate_files = defaultdict(list)

    if iteration == 2:
        for _, list_of_files in source_table.items():
            add_unique_file_to_table(list_of_files[0], destination_table)
            for file in list_of_files[1:]:
                destination_table["duplicate-files"].append(file)
        return

    # iterate through source_table and add unique files to destination_table
    for key, files in source_table.items():
        # add unique files to destinatino table
        if len(files) == 1:
            add_unique_file_to_table(files[0], destination_table)
        # add keys to duplicate files to the list
        else:
            potentially_duplicate_files[key].extend(files)

    # if the list is empty, every file we found was unique
    if not potentially_duplicate_files:
        return
    # otherwise, these files have the same size and may still be duplicates
    else:
        # clear source_table, rehash keys, and add them back to source_table
        source_table.clear()
        for _, list_of_files in potentially_duplicate_files.items():
            rehash_and_add_to_table(list_of_files, source_table, iteration)

        # recursive call
        iteration += 1
        find_duplicate_files(source_table, destination_table, iteration)


def move_files(source_table, path):
    if not os.path.exists(f"{path}/organized_files"):
        os.mkdir("organized_files")
    
    for directory_name, files in source_table.items():
        for file in files:
            source_file = f"{path}/{file}"
            destination_file = f"{path}/organized_files/{directory_name}/{file}"
            destination_directory = f"{path}/organized_files/{directory_name}"
            
            if not os.path.exists(destination_directory):
                os.mkdir(destination_directory)

            shutil.move(source_file, destination_file)


def main():
    
    sysname = os.uname()[0]
    if not sysname == "Darwin":
        exit("This program currently only works on macOS. Goodbye")

    files_in_path = []

    organized_files = defaultdict(list)
    hashed_files = defaultdict(list)

    # set up parser
    parser = argparse.ArgumentParser(
            prog="al",
            description="Al is a program that organizes a given directory by creating directories based on the file extensions found within the given path",
            # usage="%(prog)s [options] path"
            )

    # set up parser args
    parser.add_argument("path", help="path to the directory to be organized. i.e.: ~/Downloads")
    parser.add_argument("-v", "--verbose", action="store_true", help="show tree of the resulting organized folder")

    # parse arguments
    args = parser.parse_args()

    # get absolute path of directory to organize
    path = os.path.abspath(args.path)

    # ensure path passed in exists and it is a directory
    if not os.path.exists(path):
        exit(f"{path} does not exist")
    elif not os.path.isdir(path):
        exit(f"{path} is not a directory")

    # go to the directory we need to organize
    os.chdir(path)

    # obtain all files in path, save them in a list
    files_in_path = os.listdir()

    # add files in current path to a list
    for current_file in files_in_path:
        if not is_hidden_file(current_file) and not os.path.isdir(current_file):
            try:
                current_file_size = os.path.getsize(current_file)
            except OSError:
                raise Exception("Unable to obtain the current file's size")
            hashed_files[current_file_size].append(current_file)

    # begin organization process
    find_duplicate_files(hashed_files, organized_files)

    # move files
    move_files(organized_files, path)

    if args.verbose:
        print_table_as_tree(organized_files, path)


if __name__ == "__main__":
    main()
