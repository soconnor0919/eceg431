# counts occurrences of "bunny" in text files
# usage: python bunny.py <file_or_directory>
#
import sys
import os

def count_bunny(filepath):
    # Count "bunny" occurrences in a single file
    # Skips comment lines and inline comments (anything after #)
    count = 0
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip full comment lines
            if line.startswith('#'):
                continue
            # Remove inline comments (everything after #)
            if '#' in line:
                line = line[:line.index('#')]
            # Count bunny (case insensitive)
            count += line.lower().count('bunny')
    return count

def main():
    # take in one cli arg
    target = sys.argv[1]

    if os.path.isfile(target):
        # single file
        count = count_bunny(target)
        filename = os.path.basename(target)
        print(f"In {filename} I counted bunny {count} times.")

        # write count to .out file
        output_file = os.path.splitext(target)[0] + ".out"
        with open(output_file, 'w') as f:
            f.write(str(count))

    elif os.path.isdir(target):
        # is a dir- scan all .txt files
        total = 0
        if not target.endswith('/'):
            # if the dir path does not end with a slash, add one
            target += '/'

        # count bunny in all .txt files
        for file in os.listdir(target):
            # iterate through each file
            if file.endswith('.txt'):
                total += count_bunny(target + file)

        print(f"In {target} I counted bunny {total} times.")

        # write total to <dirname>.out inside directory
        dir_name = os.path.basename(target.rstrip('/'))
        output_file = target + dir_name + ".out"
        with open(output_file, 'w') as f:
            f.write(str(total))

if __name__ == "__main__":
    main()
