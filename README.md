<img src="logo.png" alt="HashTraceAI Logo" width="200">

# HashTraceAI

HashTraceAI is a lightweight tool for generating and verifying file-level manifests for machine learning models. It calculates cryptographic hashes of files in a model directory, produces a JSON manifest, and verifies those hashes to detect drift, tampering, or unintended changes.

## Purpose

HashTraceAI helps security teams verify the integrity and provenance of machine learning model artifacts in CI/CD pipelines or production deployments. By creating a manifest with cryptographic hashes of each file, teams can quickly detect drift, unauthorized modification, or corruption during storage or transmission.

## Features

- Generates a file-level manifest from any directory or Hugging Face model
- Uses SHA-256 for secure hashing
- Supports RSA-signed manifests for tamper detection
- Verifies model files against a previously generated manifest
- CLI output supports JSON or colorized text format
- Produces portable JSON output suitable for automation

## Strong Alignment with Key ISO 42001 Clauses

HashTraceAI supports secure MLOps practices aligned with ISO/IEC 42001:2023 by enabling traceability, integrity verification, and manifest-based artifact provenance checks. These features contribute to:

- **Clause 5.3, Roles and responsibilities**: Supports clear responsibility for model integrity.
- **Clause 6.1.2, Risk treatment plan**: Provides tools for monitoring changes and mitigating tampering risk.
- **Clause 8.2.1, Data and AI system integrity**: Ensures that models used in production are unchanged from those validated or reviewed.
- **Clause 8.3, Operational planning and control**: Adds traceability and reproducibility controls in the ML supply chain.

> Disclaimer: While HashTraceAI aligns with ISO 42001 goals, using it alone does not guarantee compliance. Organizations must assess it within their full AI management system.

## Installation

Clone the repository and install required dependencies:

```bash
git clone https://github.com/vsheahan/hashtraceai.git
cd hashtraceai
pip install -r requirements.txt
```

## Basic Usage

### 1. Generate Manifest from Local Directory

```bash
python3 cli.py generate ./your-model-dir --created-by "TARS" --out manifest.json
```

### 2. Verify Manifest

```bash
python3 cli.py verify ./your-model-dir --manifest manifest.json --format text
```

Use `--format json` to get structured output suitable for pipelines or logs.

### 3. Generate Manifest from Hugging Face Model

```bash
python3 cli.py generate --hf-id "bert-base-uncased" --created-by "TARS" --out manifest.json
```

### 4. Generate and Sign Manifest

```bash
python3 cli.py generate ./your-model-dir --created-by "TARS" --out manifest.json --sign private.pem
```

This will output both `manifest.json` and a digital signature file `manifest.json.sig` using the specified RSA private key. The public key is required to verify signature validity.

## Use Case Examples

| Scenario                              | Command                                                                                          | Purpose                                                |
|---------------------------------------|--------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| Generate manifest for local model     | `python3 cli.py generate ./model --created-by "TARS" --out manifest.json`                        | Hash all files in model folder                         |
| Verify model files from manifest      | `python3 cli.py verify ./model --manifest manifest.json --format text`                           | Confirm no drift or tampering                          |
| JSON output for CI/CD integration     | `python3 cli.py verify ./model --manifest manifest.json --format json`                           | Structured log output for automation                   |
| Generate manifest from Hugging Face   | `python3 cli.py generate --hf-id "bert-base-uncased" --created-by "TARS" --out manifest.json`    | Securely ingest and verify third-party model files     |
| Generate and sign a manifest          | `python3 cli.py generate ./model --created-by "TARS" --out manifest.json --sign private.pem`     | Prove authenticity with a digital signature            |

## Requirements

- Python 3.8 or newer
- `huggingface_hub` (for Hugging Face model downloads)
- `cryptography` (for RSA signing)

Install optional signing support:

```bash
pip install cryptography
```

## Output

The generated manifest is a JSON file with the following structure:

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

If `--sign` is used, a `manifest.json.sig` file is created. It can be verified using the associated public key.

## License

This project is licensed under the MIT License.