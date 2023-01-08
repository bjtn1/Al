import argparse
import os
import hashlib
from collections import defaultdict

if __name__ == "__main__":
    sysname = os.uname()[0]

    if sysname != "Darwin":
        exit("This program currently only supports mac operating systems. Goodbye.")

    parser = argparse.ArgumentParser(
            prog="Al",
            description="This tool aims to organize a given directory by removing duplicate files, and creating directories based on the file extensions found within the path passed in",
            epilog="To be done"
            )

    parser.add_argument("path", help="Path to the directory to be organized")

    args = parser.parse_args()

    directory_to_organize = os.path.abspath(args.path)
    
    if not os.path.exists(directory_to_organize):
        exit("This directory does not exist")
    elif not os.path.isdir(directory_to_organize):
        exit("This is not a directory")

    os.chdir(directory_to_organize)

    sorted_directory = sorted(os.listdir())

    organized_files = defaultdict(list)  # key = file extension, value = list of files with that extension

    hashed_by_size_table = defaultdict(list)
    semi_hashed_table = defaultdict(list)
    fully_hashed_table = defaultdict(list)

    first_byte_chunk = 1024

    def get_hash(file_object, first_iteration):
        """
        Returns the hash value of the given file object. If `first_iteration` is True, only the first 1024 bytes of the file are hashed. Otherwise, the entire file is hashed.
        """
        if first_iteration:
            file_contents = file_object.read(first_byte_chunk)
            return hashlib.sha256(file_contents).hexdigest()
        else:
            file_contents = file_object.read()
            return hashlib.sha256(file_contents).hexdigest()

    def add_to_organized_files(file):
        """
        Adds given file to the `organized_files` dictionary under the appropriate file extension key
        """
        _, file_extension = os.path.splitext(file)
        file_extension = file_extension[1:] if file_extension else "no-extension"  # if file has no extension, assign it the "no-extension" label, otherwise remove the dot
        organized_files[file_extension].append(file)

    '''Add all files to hashed_by_size_table'''
    for current_file in sorted_directory:
        is_hidden = current_file.startswith(".")
        is_directory = os.path.isdir(current_file)
        if not is_hidden and not is_directory: 
            try:
                current_file_size = os.path.getsize(current_file)
            except OSError:
                raise Exception("Unable to obtain the current file's size")
            hashed_by_size_table[current_file_size].append(current_file)

    first_hash = True

    '''Go through hashed_by_size_table'''''
    for key, list_of_files in hashed_by_size_table.items():
        if len(list_of_files) == 1:
            '''If the file is unique, we add it to organized_files'''
            add_to_organized_files((list_of_files[0]))
        else:
            '''If file is not unique, hash its first 1024 bytes and add them to semi_hashed_table'''
            for file in list_of_files:
                try:
                    with open(file, 'rb') as file_object:
                        current_hash = get_hash(file_object, first_hash)
                except OSError:
                    raise Exception("Unable to read current file")
                semi_hashed_table[current_hash].append(file)

    first_hash = False

    '''Go through semi_hashed_table'''''
    for key, list_of_files in semi_hashed_table.items():
        if len(list_of_files) == 1:
            '''If the file is unique, we add it to organized_files'''
            add_to_organized_files(list_of_files[0])
        else:
            '''If file is not unique, hash it fully and and add it to fully_hashed_table'''
            for file in list_of_files:
                try:
                    with open(file, 'rb') as file_object:
                        current_hash = get_hash(file_object, first_hash)
                except OSError:
                    raise Exception("Unable to read current file")
                fully_hashed_table[current_hash].append(file)

    '''Go through fully_hashed_table'''
    for key, list_of_files in fully_hashed_table.items():
        if len(list_of_files) == 1:
            '''If the file is unique, we add it to organized_files'''
            add_to_organized_files(list_of_files[0])
        else:
            '''Add the first file in the list to the respective place in organized_files
            Add the rest of the files to organized_files["duplicates"]'''
            add_to_organized_files(list_of_files[0])
            organized_files["duplicates"].extend(list_of_files[1:])

    for k, v in organized_files.items():
        print(f"[{k}]")
        for f in organized_files[k]:
            print(f"\t-{f}")
