# HashTraceAI

HashTraceAI is a lightweight tool for generating and verifying Software Bill of Materials (SBOMs) for machine learning models. It calculates cryptographic hashes of files in a model directory, produces a JSON SBOM, and verifies those hashes to detect drift, tampering, or unintended changes.

## Features

- Generates a file-level SBOM from any directory
- Uses SHA-256 for secure hashing
- Produces portable JSON output
- Verifies model files against a previously generated SBOM
- CLI output supports JSON or colorized text format

## Installation

Clone the repository and install required dependencies:

```bash
git clone https://github.com/vsheahan/hashtraceai.git
cd hashtraceai
pip install -r requirements.txt
```

## Basic Usage

### 1. Generate SBOM

```bash
python3 cli.py generate ./your-model-dir --created-by "TARS" --out sbom.json
```

This will create a `sbom.json` file containing hashes of all files in `./your-model-dir`.

### 2. Verify SBOM

```bash
python3 cli.py verify ./your-model-dir --sbom sbom.json --format text
```

Use `--format json` to get structured output suitable for pipelines or logs.

## Use Case Examples

| Scenario                             | Command                                                                 |
|--------------------------------------|-------------------------------------------------------------------------|
| Generate SBOM for a model folder     | `python3 cli.py generate ./model --created-by "TARS" --out sbom.json`   |
| Verify model files from SBOM         | `python3 cli.py verify ./model --sbom sbom.json --format text`          |
| JSON output for CI/CD integration    | `python3 cli.py verify ./model --sbom sbom.json --format json`          |
| Custom SBOM filename                 | `python3 cli.py generate ./model --created-by "TARS" --out model.sbom`  |

## Requirements

- Python 3.8 or newer

## Output

The generated SBOM is a JSON file with the following structure:

```json
{
  "version": "1.0",
  "created": "2025-07-05T00:30:30.152256Z",
  "created_by": "TARS",
  "files": [
    {
      "path": "model.pt",
      "sha256": "a1fff0ffefb9eace7230c24e50731f0a91c62f9cefdfe77121c2f607125dffae"
    }
  ]
}
```

## License

This project is licensed under the MIT License.