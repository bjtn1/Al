import argparse
import os
import hashlib

'''
TODO:
    1. Optimize runtime and space complexity
    2. Implement better documentation
    3. Implement program to be run on the terminal
'''

if __name__ == '__main__':
    sysname = os.uname()[0]

    if sysname != 'Darwin':
        exit('This program currently only supports mac operating systems. Goodbye.')

    parser = argparse.ArgumentParser(
            prog="Al",
            description="This tool aims to organize a given directory by removing duplicate files, and creating directories based on the file extensions found within the path passed in",
            epilog="To be done"
            )

    parser.add_argument("path", help="Path to the directory to be organized")

    args = parser.parse_args()

    directory_to_organize = os.path.abspath(args.path)
    
    if not os.path.exists(directory_to_organize):
        exit('This directory does not exist')
    elif not os.path.isdir(directory_to_organize):
        exit('This is not a directory')

    os.chdir(directory_to_organize)
    sorted_directory = sorted(os.listdir())

    organized_files = {}

    '''
    We'll use this set to store every file that we see and make comparison faster
    '''
    seen_files = {}

    for current_file in sorted_directory:
        '''
        Skip over hidden files and directories.
        '''
        if current_file.startswith('.') or os.path.isdir(current_file): 
            continue
        else:
            '''
            Get the file extension of the current file. This will be used as the key in the hash table
            '''
            current_file_name, current_file_extension = os.path.splitext(current_file)

            '''
            Add this file's hash to the set if we have permission to read it. Otherwise continue
            '''
            if os.access(current_file, os.R_OK):
                with open(current_file, 'rb') as f:
                    current_file_contents = f.read()
                    current_file_hash = hashlib.sha256(current_file_contents).hexdigest()
            else:
                continue
            
            '''
            Some files (like makefiles) don't have an extension. In that case, the key will be "no-extension"
            '''
            if not current_file_extension:
                current_file_extension = 'no-extension'
            else:
                '''
                Remove the period in the file extension (.pdf -> pdf)
                '''
                current_file_extension = current_file_extension[1:]

            '''
            If the dictionary is empty or the key doesn't exist we add the key-value pair, update the set of seen files, and continue iterating
            '''
            if not organized_files or not current_file_extension in organized_files:
                organized_files.setdefault(current_file_extension, []).append(current_file)
                seen_files.setdefault(current_file_hash, current_file)
                continue
            
            '''
            At this point, the dictionary is NOT empty, and the keys are the same. We need to check if current_file already exists in the 
            list of files of this key.
            (BRUTE FORCE WAY NEEDS TO BE OPTIMIZED) TODO: OPTIMIZE THIS
            To do this, we iterate through the list and compare the hash values of the contents of every file in the list with
            current_file_hash
            '''
            if current_file_hash in seen_files:
                '''
                If we've already seen this file, add it to duplicates
                '''
                organized_files.setdefault('duplicates', []).append(current_file)
            else:
                '''
                Otherwise, add it to the hash table and update the set
                '''
                organized_files.setdefault(current_file_extension, []).append(current_file)
                seen_files.setdefault(current_file_hash, current_file)

