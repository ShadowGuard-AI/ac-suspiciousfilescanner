import argparse
import logging
import math
import os
import sys
from collections import Counter

import filetype
import yara

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# YARA rules directory (can be changed via command line)
DEFAULT_YARA_RULES_DIR = "yara_rules"

def calculate_entropy(data):
    """Calculates the entropy of a byte string.

    Args:
        data: The byte string to analyze.

    Returns:
        The entropy of the byte string.
    """
    if not data:
        return 0
    # Counter walks the data once. The loop this replaces called
    # data.count(x) for every byte value, rescanning the whole buffer
    # 256 times, which hurt on the large files this tool exists for.
    entropy = 0
    for count in Counter(data).values():
        p_x = count / len(data)
        entropy += -p_x * math.log2(p_x)
    return entropy


# I only look for the local file header signature anywhere in the raw
# bytes. That catches a ZIP appended after other data, which is the case
# I care about, but it also means four matching bytes inside unrelated
# data read as a hit. I accept that false positive here because the
# output says suspicious, not proven, and a real archive check would
# need to parse candidate offsets instead of scanning for magic.
def detect_embedded_zip(file_path):
    """Detects if a file contains an embedded ZIP archive.

    Args:
        file_path: The path to the file to analyze.

    Returns:
        True if an embedded ZIP archive is found, False otherwise.
    """
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            if b"PK\x03\x04" in content: # ZIP file signature
                return True
    except Exception as e:
        logging.error(f"Error detecting embedded ZIP in {file_path}: {e}")
        return False
    return False


def detect_long_strings(file_path, min_length=50):
    """Detects unusually long strings in a file.

    Args:
        file_path: The path to the file to analyze.
        min_length: The minimum length for a string to be considered long.

    Returns:
        A list of long strings found in the file.
    """
    long_strings = []
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            
            # errors="ignore" means this decode cannot raise, so the old
            # UnicodeDecodeError fallback under it was dead code. Dropping
            # undecodable bytes is fine here: a long unbroken printable run
            # is the signal, and broken bytes would end the run anyway.
            text = content.decode('utf-8', errors='ignore')


            current_string = ""
            for char in text:
                if char.isprintable():
                    current_string += char
                else:
                    if len(current_string) >= min_length:
                        long_strings.append(current_string)
                    current_string = ""
            # The loop only flushes a run when a non-printable byte ends
            # it, so a file that ends mid-run needs this second check or
            # its last string is silently dropped.
            if len(current_string) >= min_length:
                long_strings.append(current_string)

    except Exception as e:
        logging.error(f"Error detecting long strings in {file_path}: {e}")
    return long_strings


def analyze_file_header(file_path):
    """Analyzes the file header based on magic number.

    Args:
        file_path: The path to the file to analyze.

    Returns:
        A string describing the detected file type based on magic number,
        or None if the file type cannot be determined.
    """
    # Both the unknown case and the error case below return the same
    # "File type: Unknown" string. I keep it that way on purpose: the
    # caller prints this line either way, and the logged error is where
    # the difference lives if I ever need to chase it.
    try:
        kind = filetype.guess(file_path)
        if kind is not None:
            return f"File type: {kind.mime}"
        else:
            return "File type: Unknown"

    except Exception as e:
        logging.error(f"Error analyzing file header of {file_path}: {e}")
        return "File type: Unknown"
    

def scan_with_yara(file_path, yara_rules_dir):
    """Scans a file with YARA rules.

    Args:
        file_path: The path to the file to scan.
        yara_rules_dir: The directory containing the YARA rules.

    Returns:
        A list of YARA matches, or an empty list if no matches are found.
    """
    matches = []
    try:
        rules = compile_yara_rules(yara_rules_dir)
        if rules:
            matches = rules.match(file_path)
        else:
            logging.warning("No YARA rules loaded. Skipping YARA scan.")
    except yara.Error as e:
        logging.error(f"YARA error scanning {file_path}: {e}")
    except Exception as e:
        logging.error(f"Error scanning {file_path} with YARA: {e}")
    return matches


def compile_yara_rules(yara_rules_dir):
    """Compiles YARA rules from a directory.

    Args:
        yara_rules_dir: The directory containing the YARA rules.

    Returns:
        A compiled YARA rules object, or None if an error occurs.
    """
    # Rules are compiled on every scan. That is a deliberate trade for a
    # one-file-at-a-time CLI: no cache to keep in sync with the rules on
    # disk, and the compile cost is small next to reading the target.
    try:
        rules = {}
        for filename in os.listdir(yara_rules_dir):
            if filename.endswith(".yar") or filename.endswith(".yara"):
                filepath = os.path.join(yara_rules_dir, filename)
                try:
                    rules[filename] = filepath
                except Exception as e:
                    logging.error(f"Error compiling YARA rule {filename}: {e}")
                    return None

        if rules:
            return yara.compile(filepaths=rules)
        else:
            logging.warning(f"No YARA rules found in directory: {yara_rules_dir}")
            return None
    except yara.Error as e:
        logging.error(f"YARA compilation error: {e}")
        return None
    except Exception as e:
        logging.error(f"Error compiling YARA rules: {e}")
        return None


def setup_argparse():
    """Sets up the command-line argument parser.

    Returns:
        An argparse.ArgumentParser object.
    """
    parser = argparse.ArgumentParser(description="Scans files for suspicious characteristics.")
    parser.add_argument("file_path", help="The path to the file to scan.")
    parser.add_argument("--yara-rules-dir", default=DEFAULT_YARA_RULES_DIR, help="The directory containing YARA rules. Default: yara_rules")
    parser.add_argument("--entropy-threshold", type=float, default=6.0, help="Threshold for considering entropy as high. Default: 6.0")
    parser.add_argument("--min-string-length", type=int, default=50, help="Minimum length for considering strings as long. Default: 50")

    return parser

def main():
    """Main function to execute the file scanner."""
    parser = setup_argparse()
    args = parser.parse_args()

    file_path = args.file_path
    yara_rules_dir = args.yara_rules_dir
    entropy_threshold = args.entropy_threshold
    min_string_length = args.min_string_length

    # Input validation. Exit nonzero so a script chaining scans can tell
    # "file missing" apart from "file scanned and clean".
    if not os.path.isfile(file_path):
        logging.error(f"Error: File not found: {file_path}")
        sys.exit(1)

    if not os.path.isdir(yara_rules_dir):
        logging.warning(f"Warning: YARA rules directory not found: {yara_rules_dir}. Skipping YARA scanning.")
        # A missing rules directory downgrades the run instead of failing
        # it, because the other checks still say something useful. The
        # trade is a quieter failure: the exit code stays 0 further down
        # even though one whole scan never ran, so I rely on this warning
        # being read.
        yara_rules_dir = None # Disable YARA scanning

    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()

        # Each detector below reopens the file by path instead of taking
        # this buffer. That wastes reads, but it keeps every check usable
        # on its own. The catch I accept: if the file changes on disk
        # mid-run, the checks are no longer all looking at the same bytes.
        entropy = calculate_entropy(file_content)
        print(f"Entropy: {entropy}")
        if entropy > entropy_threshold:
            print(f"Suspicious: High entropy detected (>{entropy_threshold})")

        # Detect embedded ZIP archives
        if detect_embedded_zip(file_path):
            print("Suspicious: Embedded ZIP archive detected")

        # Detect long strings
        long_strings = detect_long_strings(file_path, min_string_length)
        if long_strings:
            print("Suspicious: Long strings detected:")
            for string in long_strings:
                # I cap the print at 100 characters because the strings
                # this hunts for can run to thousands, and the full value
                # adds nothing once the run itself is the finding.
                print(f"  - {string[:100]}...")

        # Analyze file header
        header_analysis = analyze_file_header(file_path)
        print(header_analysis)
        
        # Scan with YARA
        if yara_rules_dir:
            matches = scan_with_yara(file_path, yara_rules_dir)
            if matches:
                print("YARA Matches:")
                for match in matches:
                    print(f"  - Rule: {match.rule}, Namespace: {match.namespace}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()