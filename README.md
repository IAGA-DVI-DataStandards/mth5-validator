# MTH5 File Validator

A **standalone**, lightweight validation tool for MTH5 (Magnetotelluric HDF5) files that checks file format, structure, and metadata compliance.

This is a standalone package that **does not require** the full mth5 installation. It only depends on h5py, making it ideal for:
- Quick validation without installing the full mth5 stack
- Creating small, distributable executables (~20-30 MB)
- CI/CD pipelines and automated quality control
- Users who only need validation capabilities

## Features

- **File Format Validation**: Verify HDF5 file attributes (type, version, data level)
- **Structure Validation**: Check group hierarchy based on file version (v0.1.4 or v0.2.0)
- **Metadata Validation**: Basic metadata structure checks
- **Data Validation**: Optional check for channel data integrity
- **Lightweight**: Only depends on h5py (no scipy, numpy, obspy, etc.)
- **Multiple Interfaces**: Use as executable, Python script, or importable module
- **Flexible Output**: Human-readable reports or JSON for integration

## Installation

### Option 1: Download Pre-built Executable (No Python Required!)

Download the latest executable for your platform from the [Releases page](https://github.com/IAGA-DVI-DataStandards/mth5-validator/releases):

- **Windows**: `mth5-validator-windows-amd64.exe.zip` (extract the .exe from the .zip file)
- **Linux**: `mth5-validator-linux-amd64`
- **macOS**: `mth5-validator-macos-amd64`

No Python installation needed! Just download and run:

```bash
# Windows (extract the .zip first, then run)
mth5-validator-windows-amd64.exe validate myfile.mth5

# Linux/macOS (make executable first)
chmod +x mth5-validator-linux-amd64
./mth5-validator-linux-amd64 validate myfile.mth5
```

**Note for Windows users**: The executable is packaged in a .zip file to avoid browser download blocks. Simply extract the .exe from the .zip and run it. Windows may show a SmartScreen warning since the executable is not code-signed - click "More info" then "Run anyway" to proceed.

### Option 2: Install as Python Package

```bash
# Install from PyPI (when published)
pip install mth5-validator

# Or install from source
git clone https://github.com/IAGA-DVI-DataStandards/mth5-validator.git
cd mth5-validator
pip install -e .
```

### Option 3: Build Your Own Executable

```bash
# Clone repository
git clone https://github.com/IAGA-DVI-DataStandards/mth5-validator.git
cd mth5-validator

# Install dependencies
pip install -r requirements.txt

# Build executable
cd src
python build_standalone_validator.py

# Find executable in src/dist/
```

## Quick Start

### Using the Standalone Executable

```bash
# Basic validation
mth5-validator validate myfile.mth5

# Verbose output
mth5-validator validate myfile.mth5 --verbose

# Check data integrity (slower)
mth5-validator validate myfile.mth5 --check-data

# JSON output
mth5-validator validate myfile.mth5 --json
```

### Using as Python Module

```python
# Run the standalone script directly
python src/mth5_validator_standalone.py validate myfile.mth5
python src/mth5_validator_standalone.py validate myfile.mth5 --verbose
```

## Validation Checks

### File Format Checks

- **file.type**: Must be "MTH5"
- **file.version**: Must be "0.1.4" or "0.2.0"
- **data_level**: Must be 0, 1, or 2

### Structure Checks (v0.1.4)

```
/Survey
  ├── Stations/
  ├── Reports/
  ├── Filters/
  ├── Standards/
  ├── channel_summary (dataset)
  └── tf_summary (dataset)
```

### Structure Checks (v0.2.0)

```
/Experiment
  ├── Surveys/
  │   └── {survey_id}/
  │       ├── Stations/
  │       ├── Reports/
  │       ├── Filters/
  │       └── Standards/
  ├── Reports/
  ├── Standards/
  ├── channel_summary (dataset)
  └── tf_summary (dataset)
```

### Station/Run Structure

Each station should contain:
- One or more run groups
- Each run should contain channel datasets

### Metadata Checks

- Validates metadata attributes exist
- Checks for required mth5_type attributes
- Uses mt_metadata schemas for validation

### Data Checks (Optional)

- Verifies channels contain data
- Detects empty or all-zero channels
- Samples data without loading full arrays

## Command-Line Interface

### mth5-validator validate

Validate an MTH5 file.

**Usage:**
```bash
mth5-validator validate FILE [OPTIONS]
```

**Arguments:**
- `FILE`: Path to MTH5 file to validate

**Options:**
- `-v, --verbose`: Enable verbose output with detailed information
- `--skip-metadata`: Skip metadata validation (structure only)
- `--check-data`: Check that channels contain data (slower)
- `--json`: Output results as JSON

**Exit Codes:**
- `0`: File is valid
- `1`: File has errors or validation failed

**Examples:**

```bash
# Basic validation
mth5-validator validate data.mth5

# Detailed validation report
mth5-validator validate data.mth5 --verbose

# Full validation including data
mth5-validator validate data.mth5 --check-data --verbose

# JSON output for scripting
mth5-validator validate data.mth5 --json > report.json

# Batch validation
for file in data/*.mth5; do
    mth5-validator validate "$file" || echo "Failed: $file"
done
```

### ValidationResults Object

Results object returned by validation.

**Properties:**
- `is_valid` (bool): True if no errors
- `error_count` (int): Number of errors
- `warning_count` (int): Number of warnings
- `info_count` (int): Number of info messages
- `messages` (list): All validation messages
- `checked_items` (dict): Dictionary of validation checks performed

**Methods:**
- `print_report(include_info=False)`: Print formatted report
- `to_dict()`: Convert to dictionary
- `to_json(**kwargs)`: Convert to JSON string
- `add_error(category, message, path=None, **details)`: Add error message
- `add_warning(category, message, path=None, **details)`: Add warning message
- `add_info(category, message, path=None, **details)`: Add info message

## Use Cases

### Archive Quality Control

Check files meet archive standards:

```bash
#!/bin/bash
# qa_check_archive.sh

VALIDATOR="./mth5-validator"
ARCHIVE_DIR="$1"
FAILED_LOG="failed_files.txt"

> "$FAILED_LOG"

for mth5_file in "$ARCHIVE_DIR"/**/*.mth5; do
    echo "Checking: $mth5_file"
    if $VALIDATOR validate "$mth5_file" --check-data; then
        echo "  ✓ Valid"
    else
        echo "  ✗ Invalid"
        echo "$mth5_file" >> "$FAILED_LOG"
    fi
done

if [ -s "$FAILED_LOG" ]; then
    echo "Failed files logged to: $FAILED_LOG"
    exit 1
else
    echo "All files valid!"
    exit 0
fi
```

### Automated Testing

Use in test suites:

```bash
# test_data_validity.sh
#!/bin/bash

set -e  # Exit on first failure

for file in tests/data/*.mth5; do
    echo "Testing: $file"
    ./mth5-validator validate "$file" --verbose
done

echo "All test files are valid!"
```

## Validation Levels

### ERROR
Critical issues that indicate an invalid file:
- Missing required file attributes
- Invalid file version or type
- Missing required groups
- Corrupted file structure

### WARNING
Issues that should be reviewed but don't prevent usage:
- Missing optional metadata
- Empty summary tables
- Runs with no channels
- Missing recommended attributes

### INFO
Informational messages:
- File version and type
- Number of surveys/stations/runs
- Summary of validation checks
- Data statistics

## Performance

### Speed Considerations

- **Basic validation** (format + structure): Very fast, <1 second
- **With metadata validation**: Fast, 1-5 seconds
- **With data checking**: Slower, depends on file size (samples data efficiently)

### Large Files

For large files (>1GB), consider:

```python
# Skip data checking for speed
validator = MTH5Validator(
    file_path='large_file.mth5',
    check_data=False  # Much faster
)
```

## Building Executables

### Automated Builds (GitHub Actions)

This repository is configured with GitHub Actions to automatically build executables for Windows, Linux, and macOS on every push to main/develop branches and on tags.

**On Push**: Artifacts are uploaded and available for download from the Actions tab.

**On Tags** (e.g., `v0.1.4`): Executables are automatically attached to the GitHub Release.

The workflow file is located at [.github/workflows/build-executables.yml](.github/workflows/build-executables.yml).

### Manual Local Build

Build your own executable locally:

```bash
# Clone repository
git clone https://github.com/IAGA-DVI-DataStandards/mth5-validator.git
cd mth5-validator

# Install dependencies
pip install -r requirements.txt

# Build executable
cd src
python build_standalone_validator.py

# Executable will be in src/dist/
# - Windows: mth5-validator.exe (~20-30 MB)
# - Linux/macOS: mth5-validator (~20-30 MB)
```

### Why So Small?

Unlike the full mth5 package (~150+ MB executable), this standalone validator:
- ✓ Only depends on h5py (and numpy, which h5py needs)
- ✓ No scipy, matplotlib, pandas, obspy, mt_metadata
- ✓ Results in ~20-30 MB executables
- ✓ Fast startup and execution
- ✓ Perfect for distribution and CI/CD

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Validate MTH5 Files

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Download validator
        run: |
          wget https://github.com/IAGA-DVI-DataStandards/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
          chmod +x mth5-validator-linux-amd64
      - name: Validate files
        run: |
          for file in data/*.mth5; do
            ./mth5-validator-linux-amd64 validate "$file" || exit 1
          done
```

### Using in Scripts

```bash
#!/bin/bash
# validate_all.sh

VALIDATOR="./mth5-validator"

for file in "$@"; do
    echo "Validating: $file"
    if $VALIDATOR validate "$file" --json > "${file%.mth5}_report.json"; then
        echo "✓ Valid"
    else
        echo "✗ Invalid - see ${file%.mth5}_report.json"
    fi
done
```

## Troubleshooting

### Executable Won't Run

**Linux/macOS**: Make sure the executable has execute permissions:
```bash
chmod +x mth5-validator-linux-amd64
```

**Windows**: If Windows Defender blocks it, you may need to add an exception or download from a trusted release.

### Python Script Import Errors

If running the script directly:
```bash
pip install --upgrade h5py
```

### File Access Errors

Ensure the MTH5 file is not open in another program:
```bash
# Close any HDF5 file viewers or other programs accessing the file
# On Linux/macOS, use lsof to check:
lsof | grep myfile.mth5
```

### Large Files Are Slow

For large files (>1GB), validation can take time. Options:
```bash
# Skip data checking for faster validation
mth5-validator validate large_file.mth5  # Structure only

# Or explicitly check data (slower but thorough)
mth5-validator validate large_file.mth5 --check-data
```

## License

MIT License - See LICENSE file in mth5 repository.

## Support

- **Issues**: https://github.com/IAGA-DVI-DataStandards/mth5-validator/issues
- **Discussions**: https://github.com/IAGA-DVI-DataStandards/mth5-validator/discussions
- **Releases**: https://github.com/IAGA-DVI-DataStandards/mth5-validator/releases

## Related Projects

- **MTH5**: Full-featured MTH5 file manipulation library - [https://github.com/IAGA-DVI-DataStandards/mth5](https://github.com/IAGA-DVI-DataStandards/mth5)
- **mt_metadata**: Metadata standards for magnetotellurics - [https://github.com/IAGA-DVI-DataStandards/mt_metadata](https://github.com/IAGA-DVI-DataStandards/mt_metadata)
- **MTpy-v2**: Magnetotelluric data processing - [https://github.com/MTgeophysics/mtpy-v2](https://github.com/MTgeophysics/mtpy-v2)

## Development

### Project Structure

```
mth5-validator/
├── .github/
│   └── workflows/
│       └── build-executables.yml  # Automated builds
├── src/
│   ├── mth5_validator_standalone.py  # Main validator
│   ├── build_standalone_validator.py  # Build script
│   └── __init__.py
├── pyproject.toml  # Package configuration
├── requirements.txt  # Dependencies
├── .gitignore
└── README.md
```

### Contributing

Contributions welcome! To add new validation checks:

1. Fork the repository
2. Add check methods to `mth5_validator_standalone.py`
3. Update tests if applicable
4. Submit a pull request

### Testing Locally

```bash
# Test the script directly
cd src
python mth5_validator_standalone.py validate ../test_data/sample.mth5

# Build and test executable
python build_standalone_validator.py
dist/mth5-validator validate ../test_data/sample.mth5
```

# Example: Using MTH5 Validator in Your CI/CD

This directory contains example workflows for integrating the MTH5 validator into your own projects.

## GitHub Actions Examples

### Basic Validation on Push

Create `.github/workflows/validate-mth5.yml` in your repository:

```yaml
name: Validate MTH5 Files

on:
  push:
    paths:
      - '**.mth5'
  pull_request:
    paths:
      - '**.mth5'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Download MTH5 Validator
        run: |
          wget https://github.com/IAGA-DVI-DataStandards/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
          chmod +x mth5-validator-linux-amd64
      
      - name: Validate all MTH5 files
        run: |
          for file in $(find . -name "*.mth5"); do
            echo "Validating: $file"
            ./mth5-validator-linux-amd64 validate "$file" --verbose || exit 1
          done
```

### Validation with Artifacts

Save validation reports as artifacts:

```yaml
name: Validate and Report

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Download MTH5 Validator
        run: |
          wget https://github.com/IAGA-DVI-DataStandards/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
          chmod +x mth5-validator-linux-amd64
      
      - name: Create reports directory
        run: mkdir -p reports
      
      - name: Validate and create reports
        run: |
          for file in data/*.mth5; do
            filename=$(basename "$file" .mth5)
            ./mth5-validator-linux-amd64 validate "$file" --json > "reports/${filename}_report.json"
          done
      
      - name: Upload validation reports
        uses: actions/upload-artifact@v4
        with:
          name: validation-reports
          path: reports/
```

### Matrix Validation (Multiple Platforms)

Test on multiple operating systems:

```yaml
name: Multi-Platform Validation

on: [push, pull_request]

jobs:
  validate:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        include:
          - os: ubuntu-latest
            validator: mth5-validator-linux-amd64
          - os: windows-latest
            validator: mth5-validator-windows-amd64.exe
            validator_zip: mth5-validator-windows-amd64.exe.zip
          - os: macos-latest
            validator: mth5-validator-macos-amd64
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Download validator (Linux/macOS)
        if: runner.os != 'Windows'
        run: |
          wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/${{ matrix.validator }}
          chmod +x ${{ matrix.validator }}
      
      - name: Download and extract validator (Windows)
        if: runner.os == 'Windows'
        run: |
          curl -L -o ${{ matrix.validator_zip }} https://github.com/MTgeophysics/mth5-validator/releases/latest/download/${{ matrix.validator_zip }}
          Expand-Archive -Path ${{ matrix.validator_zip }} -DestinationPath . -Force
      
      - name: Validate files
        shell: bash
        run: |
          for file in tests/data/*.mth5; do
            ./${{ matrix.validator }} validate "$file" --verbose
          done
```

## GitLab CI Example

`.gitlab-ci.yml`:

```yaml
stages:
  - validate

validate_mth5:
  stage: validate
  image: ubuntu:latest
  before_script:
    - apt-get update && apt-get install -y wget
    - wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
    - chmod +x mth5-validator-linux-amd64
  script:
    - |
      for file in data/*.mth5; do
        echo "Validating: $file"
        ./mth5-validator-linux-amd64 validate "$file" --verbose
      done
  artifacts:
    when: always
    paths:
      - "*.json"
```

## Jenkins Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Download Validator') {
            steps {
                sh '''
                    wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
                    chmod +x mth5-validator-linux-amd64
                '''
            }
        }
        
        stage('Validate') {
            steps {
                sh '''
                    for file in data/*.mth5; do
                        ./mth5-validator-linux-amd64 validate "$file" --json > "${file%.mth5}_report.json"
                    done
                '''
            }
        }
        
        stage('Archive Reports') {
            steps {
                archiveArtifacts artifacts: '*_report.json', fingerprint: true
            }
        }
    }
}
```

## Docker Example

```dockerfile
FROM ubuntu:22.04

# Install wget
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# Download validator
RUN wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64 \
    && chmod +x mth5-validator-linux-amd64 \
    && mv mth5-validator-linux-amd64 /usr/local/bin/mth5-validator

# Validate files in mounted volume
ENTRYPOINT ["mth5-validator"]
CMD ["--help"]
```

Usage:
```bash
docker build -t mth5-validator .
docker run -v $(pwd)/data:/data mth5-validator validate /data/file.mth5
```

## Pre-commit Hook Example

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-mth5
        name: Validate MTH5 files
        entry: ./scripts/validate-mth5-hook.sh
        language: script
        files: \.mth5$
```

`scripts/validate-mth5-hook.sh`:
```bash
#!/bin/bash

VALIDATOR="./mth5-validator-linux-amd64"

if [ ! -f "$VALIDATOR" ]; then
    echo "Downloading validator..."
    wget -q https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
    chmod +x mth5-validator-linux-amd64
fi

for file in "$@"; do
    if [[ $file == *.mth5 ]]; then
        echo "Validating: $file"
        $VALIDATOR validate "$file" || exit 1
    fi
done
```

## Tips

1. **Cache the validator**: Download once and cache to speed up workflows
2. **Pin versions**: Use specific release tags instead of `latest` for reproducibility
3. **Parallel validation**: Use job matrices to validate multiple files in parallel
4. **Conditional validation**: Only validate changed files to save time
5. **Fail fast**: Set `exit 1` on validation errors to stop workflows early

## Verification

Always verify downloaded executables using checksums:

```bash
# Download executable and checksum
wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64
wget https://github.com/MTgeophysics/mth5-validator/releases/latest/download/mth5-validator-linux-amd64.sha256

# Verify
sha256sum -c mth5-validator-linux-amd64.sha256
```

