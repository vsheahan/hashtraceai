
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
- Uses **password-encrypted private keys** for secure signing operations
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

You will be prompted to create and confirm a password for the private key.

```bash
python3 cli.py keys --name my_key --out-dir keys
```
Keep your private_key.pem file and its password secret! The public_key.pem can be distributed freely.

### 2. Generate and Sign a Manifest

Next, generate a manifest for your model. The --sign flag will use your private key to create a digital signature. You will be prompted for the password you created in Step 1.

```bash
python3 cli.py generate --path ./your-model-dir --created-by "Your Name" --model-name "My Model" --model-version "1.0" --sign-key keys/my_key.pem
```
This command creates two files:
manifest.json: The list of files and their hashes.
manifest.json.sig: The digital signature for manifest.json.

### 3. Verify the Manifest and its Signature

Finally, anyone with the public key can verify the integrity of the model files and the authenticity of the manifest. This command checks both that the files haven't changed and that the signature is valid.

```bash
python3 cli.py verify --manifest-file your-model-dir/My\ Model_1.0_manifest.json --public-key keys/my_key.pub
```

### Use Case Examples

| Scenario                              | Command                                                                                             | Purpose                                                                |
|---------------------------------------|------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| Generate an encrypted key pair        | `python3 cli.py keys generate`                                                                       | Create a secure, password-protected key pair for signing.              |
| Generate and sign a manifest          | `python3 cli.py generate ./model --created-by "<TARS>" --sign private.pem`                           | Prove authenticity with a digital signature, requires password.        |
| Verify files and signature            | `python3 cli.py verify ./model --manifest manifest.json --verify-sig public.pem`                       | Confirm that files are unchanged and the manifest is authentic.        |
| Generate manifest (no signature)      | `python3 cli.py generate ./model --created-by "<TARS>" --out manifest.json`                           | Hash all files in model folder for basic integrity checks.             |
| Verify files only (no signature)      | `python3 cli.py verify ./model --manifest manifest.json --format text`                              | Confirm no file drift or tampering without checking authenticity.      |
| Generate manifest from Hugging Face   | `python3 cli.py generate --hf-id "bert-base-uncased" --created-by "<TARS>" --out manifest.json`       | Securely ingest and verify third-party model files.                    |
## Hugging Face Downloader

You can also download a model from the Hugging Face Hub and generate a manifest for it in one command:

```bash
python3 hf_downloader.py --model-id "distilbert-base-uncased" --created-by "Your Name" --sign-key keys/my_key.pem --model-version "1.0"
| JSON output for CI/CD integration     | `python3 cli.py verify ./model --manifest manifest.json --format json`                              | Get structured log output for automation.      

This will download the specified model, and then use the cli.py tool to generate a manifest for it.                        |

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
    "model_name": "My Model",
    "model_version": "1.0",
    "created_by": "Your Name",
    "timestamp_utc": "2025-07-06T23:50:00.123456+00:00",
    "timestamp_local": "2025-07-06T19:50:00.123456",
    "files": [
        {
            "name": "file1.txt",
            "path": "file1.txt",
            "sha256": "..."
        },
        {
            "name": "image.png",
            "path": "data/image.png",
            "sha256": "..."
        }
    ],
    "signature": "..."
}
```

If `--sign` is used, a `manifest.json.sig` file is created. It can be verified using the associated public key.

## License

This project is licensed under the MIT License.