<img src="logo.png" alt="HashTraceAI Logo" width="200">

# HashTraceAI

HashTraceAI is a lightweight tool for generating and verifying file-level manifests for machine learning models. It calculates cryptographic hashes of files in a model directory, produces a JSON manifest, and verifies those hashes to detect drift, tampering, or unintended changes.

## Purpose

HashTraceAI helps security teams verify the integrity and provenance of machine learning model artifacts in CI/CD pipelines or production deployments. By creating a manifest with cryptographic hashes of each file, teams can quickly detect drift, unauthorized modification, or corruption during storage or transmission.

## Features

- Generates a file-level manifest from any directory
- Uses SHA-256 for secure hashing
- Produces portable JSON output
- Verifies model files against a previously generated manifest
- Supports Hugging Face model download and manifest generation
- CLI output supports JSON or colorized text format

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

This will create a `manifest.json` file containing hashes of all files in `./your-model-dir`.

### 2. Verify Manifest

```bash
python3 cli.py verify ./your-model-dir --manifest manifest.json --format text
```

Use `--format json` to get structured output suitable for pipelines or logs.

### 3. Generate Manifest from Hugging Face Model

```bash
python3 cli.py generate --hf-id "bert-base-uncased" --created-by "TARS" --out manifest.json
```

This downloads the Hugging Face model locally, computes file hashes, and outputs `manifest.json`.

### 4. Verify a Hugging Face Snapshot

```bash
python3 cli.py verify ~/.cache/huggingface/hub/models--bert-base-uncased/snapshots/<snapshot-id> --manifest manifest.json --format text
```

This command checks that the local cached Hugging Face model files match the manifest you generated earlier.

## Use Case Examples

| Scenario                             | Command                                                                                     | Purpose                                                |
|--------------------------------------|---------------------------------------------------------------------------------------------|--------------------------------------------------------|
| Generate manifest for local model    | `python3 cli.py generate ./model --created-by "TARS" --out manifest.json`                   | Hash all files in model folder                         |
| Verify model files from manifest     | `python3 cli.py verify ./model --manifest manifest.json --format text`                      | Confirm no drift or tampering                          |
| JSON output for CI/CD integration    | `python3 cli.py verify ./model --manifest manifest.json --format json`                      | Structured log output for automation                   |
| Generate manifest from Hugging Face  | `python3 cli.py generate --hf-id "bert-base-uncased" --created-by "TARS" --out manifest.json` | Securely ingest and verify third-party model files     |
| Verify Hugging Face snapshot         | `python3 cli.py verify ~/.cache/.../snapshots/<id> --manifest manifest.json --format text`  | Re-check cached remote models for integrity            |
| Custom manifest filename             | `python3 cli.py generate ./model --created-by "TARS" --out model.manifest`                  | Store under project-specific naming conventions        |

## Requirements

- Python 3.8 or newer

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

## Standards Alignment

HashTraceAI supports AI model integrity and provenance assurance in ways that align with several key clauses of ISO/IEC 42001:2023 (AI Management System Standard). It can serve as a technical control in AI governance programs focused on traceability, tamper detection, and secure model deployment.

### Strong Alignment with Key ISO 42001 Clauses

| ISO 42001 Clause                              | Alignment                                                                 |
|-----------------------------------------------|---------------------------------------------------------------------------|
| **6.1.2 Risk Assessment and Treatment**        | Detects and mitigates risks of model drift, tampering, or corruption.     |
| **8.4.2 Integrity of AI Artifacts**            | Verifies cryptographic hashes of files to ensure model integrity.         |
| **8.4.3 Provenance and Lifecycle Management**  | Adds traceable metadata to manifests for model version tracking.          |
| **8.5.2 Transparency of AI Systems**           | Provides visibility into model contents through JSON manifests.           |
| **8.6.1 Secure AI Development and Deployment** | Supports secure ingestion and deployment of local and third-party models. |
| **9.1 Monitoring and Measurement**             | Enables audit-friendly verification with machine-readable output.         |

> **Disclaimer:** While HashTraceAI supports several technical practices aligned with ISO/IEC 42001, full compliance requires additional organizational policies, governance frameworks, and risk management processes beyond the scope of this tool.

## License

This project is licensed under the MIT License.