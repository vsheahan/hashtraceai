# HashTrace.ai

HashTrace.ai is a lightweight CLI tool for generating and verifying Software Bills of Materials (SBOMs) for AI artifacts. It helps establish provenance and integrity for machine learning models and other components in the AI/ML supply chain.

## Project Purpose

HashTrace.ai addresses a growing need for AI transparency and integrity checking. As AI models are shared, fine-tuned, and deployed across environments, verifying the origin and content of those artifacts becomes critical for trust, reproducibility, and security.

## Features

- Generate an SBOM for all files in a given directory  
- Verify a directory against a previously generated SBOM  
- Choose between `json` or human-readable `text` output  
- Simple CLI interface with colorized output for visibility  

## Example

```
# Create a model directory and file
mkdir mymodel
echo "example weights" > mymodel/model.pt

# Generate SBOM
python3 cli.py generate ./mymodel --created-by "TARS" --out sbom.json

# Verify integrity of the directory
python3 cli.py verify ./mymodel --sbom sbom.json --format text
```

## Output

`sbom.json` will look like this:

```
{
  "version": "1.0",
  "created": "2025-07-04T20:00:00Z",
  "created_by": "TARS",
  "files": [
    {
      "path": "model.pt",
      "sha256": "abcdef1234567890..."
    }
  ]
}
```

## Requirements

- Python 3.7 or higher

Install dependencies with:

```
pip install -r requirements.txt
```

## Development

To run tests:

```
pytest
```

To format code:

```
black .
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.