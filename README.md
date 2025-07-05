# HashTraceAI

HashTraceAI is a lightweight Python-based tool to generate and verify a Software Bill of Materials (SBOM) for AI/ML models. It ensures the integrity of model artifacts by creating cryptographic fingerprints (SHA-256) of each file and verifying them against a known-good SBOM file.

## Features

- Generates a JSON-formatted SBOM for any model directory
- Verifies the current state of model files against a stored SBOM
- Highlights missing or tampered files using SHA-256 hash comparison
- Outputs verification results in colorized terminal output or JSON format

## Installation

Clone the repository and install the requirements:

```bash
git clone https://github.com/vsheahan/hashtraceai.git
cd hashtraceai
pip install -r requirements.txt
```

## Usage

### 1. Prepare Your Model

Make sure your model files are in a directory, for example:

```
my_model/
├── config.json
├── model.pt
└── tokenizer.json
```

### 2. Generate an SBOM

Use the `generate` command to create an SBOM from your model directory:

```bash
python3 cli.py generate ./my_model --created-by "TARS" --out sbom.json
```

- `./my_model` is the path to your model directory
- `--created-by` is metadata for the SBOM (your name, org, or alias)
- `--out` is the destination file for the SBOM (default is `sbom.json`)

### 3. Verify an SBOM

To verify the integrity of a model directory using a saved SBOM:

```bash
python3 cli.py verify ./my_model --sbom sbom.json --format text
```

- `--sbom` is the path to your SBOM file (default is `sbom.json`)
- `--format` can be `text` (colorized CLI) or `json` (machine-readable)

### Example Output (text format)

```
All files verified successfully.
```

Or if mismatches are found:

```
Verification failed:
  [MISSING] tokenizer.json
  [MISMATCH] model.pt
```

### Example Output (JSON format)

```json
{
  "result": "fail",
  "mismatches": [
    { "type": "missing", "file": "tokenizer.json" },
    { "type": "hash_mismatch", "file": "model.pt" }
  ]
}
```

## Output

The SBOM is a JSON file with metadata and file checksums. Example:

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

## Requirements

- Python 3.8+
- `argparse`
- Standard Library only (no external dependencies)

## License

MIT License. See `LICENSE` for details.