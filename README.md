<p align="left">
  <img src="logo.png" alt="HashTraceAI Logo" width="250">
</p>

<p align="left">
  <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Python" src="https://img.shields.io/badge/python-3.8%2B-blue">
  <img alt="Hugging Face" src="https://img.shields.io/badge/integrates-HuggingFace-blue">
  <img alt="MLflow" src="https://img.shields.io/badge/integrates-MLflow-blue">
</p>

# HashTraceAI

HashTraceAI is a lightweight tool for generating and verifying file-level manifests for machine learning models. It calculates cryptographic hashes of files in a model directory, produces a JSON manifest, and verifies those hashes to detect drift, tampering, or unintended changes.

## Purpose

HashTraceAI helps security teams verify the integrity and provenance of machine learning model artifacts in CI/CD pipelines or production deployments. By creating a manifest with cryptographic hashes of each file, teams can quickly detect drift, unauthorized modification, or corruption during storage or transmission.

## Features

- Generates a file-level manifest from any directory or model hub (Hugging Face, MLflow)
- Uses **SHA-256** for secure hashing
- Supports **RSA-signed manifests** for tamper detection and authenticity verification
- Requires **password-encrypted private keys** for secure signing operations
- Verifies model files against a previously generated manifest
- Verifies the manifest's digital signature to prove authenticity
- CLI output supports JSON or colorized text format
- Produces portable JSON output suitable for automation

## Strong Alignment with Key ISO 42001 Clauses

HashTraceAI supports secure MLOps practices aligned with ISO/IEC 42001:2023 by enabling traceability, integrity verification, provenance validation, and cryptographic signature verification of model artifacts. These features contribute to:

- **Clause 5.3 – Roles and responsibilities** Ensures teams can clearly define and enforce responsibility for model integrity and approval workflows.

- **Clause 6.1.2 – Risk treatment plan** Supports the detection of unauthorized model drift or tampering via manifest verification and optional digital signatures.

- **Clause 7.5 – Documented information** Allows for automated and cryptographically verifiable documentation of model versions and components in regulated environments.

- **Clause 8.2.1 – Data and AI system integrity** Confirms that deployed models match the validated and approved versions using strong file-level hashing and signature verification.

- **Clause 8.3 – Operational planning and control** Integrates into CI/CD pipelines to enforce provenance and integrity checks for models sourced internally or from third parties (e.g., Hugging Face, MLflow).

> **Disclaimer:** While HashTraceAI aligns with ISO 42001 principles, its use alone does not ensure compliance. Organizations should evaluate it as part of a broader AI management and risk governance program.

## Installation

Clone the repository and install required dependencies:

```bash
git clone https://github.com/vsheahan/hashtraceai.git
cd hashtraceai
pip install -r requirements.txt

```
## Recommended Workflow

Here is the recommended three-step process for ensuring maximum security and authenticity.

### 1. Generate an Encrypted Key Pair

First, create a password-protected private key and a corresponding public key. The private key will be used for signing, and the public key will be used for verification.

You must create and confirm a password for the private key. Empty passwords are not allowed.

```bash
python3 cli.py keys generate --priv private_key.pem --pub public_key.pem
```
Keep your private_key.pem file and its password secret! The public_key.pem can be distributed freely.

### 2. Generate and Sign a Manifest

Next, generate a manifest for your model. The --sign flag will use your private key to create a digital signature. You will be prompted for the password you created in Step 1.

```bash
python3 cli.py generate --path ./your-model-dir --created-by "<TARS>" --sign-key private_key.pem
```
This command creates two files:
manifest.json: The list of files and their hashes.
manifest.json.sig: The digital signature for manifest.json.

### 3. Verify the Manifest and its Signature

Finally, anyone with the public key can verify the integrity of the model files and the authenticity of the manifest. This command checks both that the files haven't changed and that the signature is valid.

```bash
python3 cli.py verify ./your-model-dir --manifest manifest.json --verify-sig public_key.pem
```

### Use Case Examples

| Scenario                              | Command                                                                                             | Purpose                                                                |
|---------------------------------------|------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| Generate an encrypted key pair        | `python3 cli.py keys generate`                                                                       | Create a secure, password-protected key pair for signing.              |
| Generate and sign a manifest          | `python3 cli.py generate --path ./model --created-by "<TARS>" --sign-key private.pem`                           | Prove authenticity with a digital signature, requires password.        |
| Verify files and signature            | `python3 cli.py verify ./model --manifest manifest.json --verify-sig public.pem`                       | Confirm that files are unchanged and the manifest is authentic.        |
| Generate manifest (no signature)      | `python3 cli.py generate --path ./model --created-by "<TARS>" --out manifest.json`                           | Hash all files in model folder for basic integrity checks.             |
| Verify files only (no signature)      | `python3 cli.py verify ./model --manifest manifest.json --format text`                              | Confirm no file drift or tampering without checking authenticity.      |
| Generate manifest from Hugging Face   | `python3 cli.py generate --hf-id "bert-base-uncased" --created-by "<TARS>" --out manifest.json`       | Securely ingest and verify third-party model files.                    |
| Generate manifest from MLflow         | `python3 cli.py generate --mlflow-uri "runs:/<RUN_ID>/model" --created-by "<TARS>" --out manifest.json`| Trace artifacts from internal model tracking systems.                  |
| JSON output for CI/CD integration     | `python3 cli.py verify ./model --manifest manifest.json --format json`                              | Get structured log output for automation.                              |

## Requirements

- Python 3.8 or newer
- `huggingface_hub` (for Hugging Face model downloads)
- `cryptography` (for RSA signing)
- `mlflow` (for MLflow model artifacts)
- `colorama`

## Output

The generated manifest is a JSON file with the following structure:

```json
{
  "version": "1.0",
  "created": "2025-07-05T00:30:30.152256Z",
  "created_by": "<TARS>",
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