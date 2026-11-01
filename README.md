![Banner](banner.png)

# ac-SuspiciousFileScanner
Scans one file for indicators of suspicious characteristics: high entropy, an embedded ZIP signature, unusually long printable strings, a file type from magic bytes, and YARA rule matches.

## Install
```
git clone https://github.com/ShadowGuard-AI/ac-suspiciousfilescanner
cd ac-suspiciousfilescanner
pip install -r requirements.txt
```

## Usage
```
python3 main.py FILE_PATH [--yara-rules-dir DIR] [--entropy-threshold NUMBER] [--min-string-length NUMBER]
```

## Parameters
- `FILE_PATH`: the path to the file to scan.
- `-h`: show help message and exit.
- `--yara-rules-dir`: directory containing YARA rules. Default: `yara_rules`.
- `--entropy-threshold`: threshold for considering entropy as high. Default: 6.0.
- `--min-string-length`: minimum length for considering strings as long. Default: 50.

## Verified behavior
- A missing input file exits 1.
- If the YARA rules directory does not exist, the run logs a warning and skips YARA scanning, and the other checks still run.
- Printed long strings are capped at 100 characters.
- The ZIP check is a search for the `PK\x03\x04` signature bytes in the file, not a parsed archive check, so a hit means a signature was found, not a proven embedded archive.
- Live run not possible in this environment: the `filetype` and `yara` packages are not installed here and installs are not permitted in this wave. The parameter list above is taken from the argument parser in `main.py`, and the file compiles cleanly.

## License
MIT License, see LICENSE.
