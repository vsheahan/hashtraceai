# HashTraceAI

A simple tool for creating and verifying file manifests.

## Recommended Workflow

1.  **Generate a key pair:**

    ```bash
    python3 cli.py keys --name my_key --out-dir keys
    ```

    This will create `my_key.pub` and `my_key.pem` in the `keys` directory and add the public key to `trusted_keys.json`.

2.  **Generate a manifest:**

    ```bash
    python3 cli.py generate --directory my_project --private-key keys/my_key.pem --output-file my_project/manifest.json
    ```

    This will scan the `my_project` directory, create a `manifest.json` file inside it with UTC and local timestamps, and sign the file list with your private key.

3.  **Verify a manifest:**

    You can verify the manifest using either the public key file or the trusted key name.

    * Using the public key file:
        ```bash
        python3 cli.py verify --manifest-file my_project/manifest.json --public-key keys/my_key.pub
        ```

    * Using the trusted key name:
        ```bash
        python3 cli.py verify --manifest-file my_project/manifest.json --trusted-key my_key
        ```

    This will verify the signature and check the hashes of all the files listed in the manifest.

## Manifest File Structure

The `manifest.json` file has the following structure. **Note:** The `signature` field only covers the `files` list and does not include the timestamps.

```json
{
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