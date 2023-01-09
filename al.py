#!/usr/bin/env python3

import argparse
import os
import hashlib
from collections import defaultdict

byte_chunk = 1024

def is_macOS(sysname):
    """Returns true if current system is macOS, false otherwise. Takes in parameter `sysname` which is a string representing current system's name"""
    return sysname == "Darwin"


def path_exists(path):
    """Returns true if path exists, false otherwise. Takes in param `path` which is a string representing the path whose existence will be checked"""
    return os.path.exists(path)


def is_directory(path):
    """Returns true if `path` is a directory. Param `path` is a string representing the path to be checked"""
    return os.path.isdir(path)


def is_hidden_file(file):
    """Returns true if `file` starts with `.`"""
    return file.startswith(".")


def print_table(source_table):
    """Prints the keys and values in `source_table` in alphabetical order"""
    source_table = {k: source_table[k] for k in sorted(source_table)}
    source_table = {k: sorted(v) for k, v in source_table.items()}
    for k, _ in source_table.items():
        print(f"[{k}]")
        for f in source_table[k]:
            print(f"\t-{f}")


def get_hash(file_object, iteration):
    """Returns the hash value of the given file object. If `first_iteration` is True, only the first 1024 bytes of the file are hashed. Otherwise, the entire file is hashed"""
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
    # we know we're done finding duplicates if:
    #   iteration == 2
    #   after adding all unique files to destination_table, there are no duplicate files in source_table
    #   after adding unique files to destination_table, the list is empty

    if iteration == 2:
        # TODO: add one dupe to destination_table, and the rest to destination_table["duplicates"]
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


def main():
    files_in_path = []

    organized_files = defaultdict(list)
    hashed_files = defaultdict(list)

    sysname = os.uname()[0]
    if not is_macOS(sysname):
        exit("This program currently only works on macOS. Goodbye")

    # set up parser
    parser = argparse.ArgumentParser(
            prog="Al",
            description="This tool aims to organize a given directory by removing duplicate files, and creating directories based on the file extensions found within the path passed in",
            epilog="To be done"
            )

    # # set up parser args
    parser.add_argument("path", help="Path to the directory to be organized")

    # # parse arguments
    args = parser.parse_args()

    # # get absolute path of directory to organize
    path = os.path.abspath(args.path)

    # # ensure path passed in exists and it is a directory
    if not path_exists(path):
        exit(f"{path} does not exist")
    elif not is_directory(path):
        exit(f"{path} is not a directory")

    # go to the directory we need to organize
    os.chdir(path)

    # obtain all files in path, save them in a list
    files_in_path = os.listdir()

    # add files in current path to a list
    for current_file in files_in_path:
        if not is_hidden_file(current_file) and not is_directory(current_file):
            try:
                current_file_size = os.path.getsize(current_file)
            except OSError:
                raise Exception("Unable to obtain the current file's size")
            hashed_files[current_file_size].append(current_file)

    # begin organization process
    find_duplicate_files(hashed_files, organized_files)

    print_table(organized_files)


if __name__ == "__main__":
    main()
