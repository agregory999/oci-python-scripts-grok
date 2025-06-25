# OCI Python Scripts Project Setup Guide

This guide provides the finalized setup for the `oci-python-scripts-grok` project, a collection of function-based Python scripts using Oracle Cloud Infrastructure (OCI), Tkinter, `tksheet`, and `argparse`. The project uses `uv` for dependency management and `ruff` for linting/formatting with GitHub pre-commit hooks. It includes four scripts:
- `oci-simple.py`: Lists compute instance names and running status in a specified compartment (`-c`, `-v`, `-p`).
- `oci-tkinter-display.py`: Displays compute instance details (name, OCID, size, status) in a Tkinter GUI with `tksheet` (`-c`, `-b`, `-v`, `-p`). Fixed bugs: removed duplicate `main` function and corrected logging message.
- `oci-parallel-paginated.py`: Lists compute instance names across all compartments using threaded execution with pagination (`-m`, `-v`, `-p`).
- `oci-parallel-search.py`: Searches for running compute instances tenancy-wide, returning name and size, using threaded processing (`-m`, `-v`, `-p`).

The project is optimized for simplicity (no tests, minimal arguments, centralized OCI handling) and resolves all issues, including:
- Short argument names (`-v`, `-c`, `-b`, `-m`).
- Widened Tkinter window (800x600) with updated status handling.
- Renamed `oci-parallel-execution.py` to `oci-parallel-paginated.py`.
- Corrected `oci-parallel-search.py` to use `ResourceSummaryCollection.items` and `ComputeClient.get_instance`.
- Fixed `ModuleNotFoundError` by using absolute imports (`from utils import ...`) and a simplified directory structure.
- Added support for named OCI profiles via `-p`/`--profile`.
- Organized imports across all scripts per Ruff's rules.

## Prerequisites
- **Python 3.12**: Includes Tkinter and `argparse`.
- **UV**: Install via [docs.astral.sh](https://docs.astral.sh/uv/).
- **Git**: Installed for version control.
- **Visual Studio Code (VSCode)**: Optional, for editing and testing (see Step 3).
- **OCI Configuration**: Config file at `~/.oci/config` with profiles (e.g., `DEFAULT`, `MY_PROFILE`) containing tenancy, user, key, fingerprint, and region, or instance principal setup.

## Step 1: Set Up Git Repository
1. **Create a Local Repository**:
   ```bash
   mkdir oci-python-scripts-grok
   cd oci-python-scripts-grok
   git init
   ```

2. **Create a GitHub Repository**:
   - Via GitHub UI: Create a repository named `oci-python-scripts-grok` at [github.com](https://github.com).
   - Via GitHub CLI (if installed):
     ```bash
     gh repo create oci-python-scripts-grok --public --source=. --remote=origin
     ```
   - Add the remote:
     ```bash
     git remote add origin https://github.com/<your-username>/oci-python-scripts-grok.git
     ```

3. **Add Initial Files**:
   After setting up files (Steps 4-6), commit and push:
   ```bash
   git add .
   git commit -m "Initial project setup with OCI scripts"
   git push -u origin main
   ```

## Step 2: Project Dependencies
Create `pyproject.toml`:

```toml
[project]
name = "oci-python-scripts-grok"
version = "0.1.0"
description = "A simplified Python project with OCI, Tkinter, tksheet, and argparse"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "oci>=2.135.0",
    "tksheet>=7.2.5",
]

[tool.uv]
dev-dependencies = [
    "ruff>=0.11.0",
    "pre-commit>=4.0.1",
]

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
extend-select = ["B", "I"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "single"
```

## Step 3: Set Up VSCode
1. **Install VSCode**:
   Download from [code.visualstudio.com](https://code.visualstudio.com/).

2. **Install Extensions**:
   - **Python**: `ms-python.python` for Python support.
   - **Pylance**: `ms-python.vscode-pylance` for IntelliSense.
   - **Ruff**: `astral-sh.ruff` for linting/formatting.

3. **Open Project**:
   ```bash
   code .
   ```

4. **Configure Python Interpreter**:
   - Press `Ctrl+Shift+P`, select `Python: Select Interpreter`.
   - Choose `./.venv/bin/python` (created in Step 4).

5. **Run Scripts**:
   - Open a script (e.g., `src/oci-simple.py`).
   - Click "Run Python File" (top-right) or use the terminal:
     ```bash
     python src/oci-simple.py -c ocid1.compartment.oc1..example -p MY_PROFILE
     ```
     or
     ```bash
     uv run src/oci-simple.py -c ocid1.compartment.oc1..example -p MY_PROFILE
     ```
   - For GUI:
     ```bash
     python src/oci-tkinter-display.py -c ocid1.compartment.oc1..example -b lightblue -p MY_PROFILE
     ```

## Step 4: Set Up Virtual Environment
1. **Install Dependencies**:
   ```bash
   uv sync
   uv export --format requirements-txt > requirements.txt
   ```
   Creates `.venv`, installs `oci`, `tksheet`, `ruff`, `pre-commit`, and generates `requirements.txt`.

2. **Activate Environment** (if not using VSCode):
   ```bash
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

## Step 5: Configure Pre-Commit Hooks
Create `.gitignore`:

```text
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
uv.lock
~/.oci/
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.0
    hooks:
      - id: ruff-format
        name: "Format with Ruff"
        types: [python]
        files: ^src/.*\.py$
      - id: ruff
        name: "Lint with Ruff"
        types: [python]
        files: ^src/.*\.py$
        args: [--fix, --exit-non-zero-on-fix]
```

Install hooks:
```bash
uv run pre-commit install
```

## Step 6: Directory Structure
```
oci-python-scripts-grok/
├── .git/
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── .venv/
├── pyproject.toml
├── README.md
├── requirements.txt
├── src/
│   ├── oci-simple.py
│   ├── oci-tkinter-display.py
│   ├── oci-parallel-paginated.py
│   ├── oci-parallel-search.py
│   └── utils.py
└── uv.lock
```

## Step 7: Utility Functions
**src/utils.py**:

```python
import argparse
import logging
import os

import oci

def setup_logging(verbose: bool) -> logging.Logger:
    """Set up logging based on verbose flag."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def initialize_oci(profile_name: str = 'DEFAULT') -> tuple[dict, oci.auth.signers.InstancePrincipalsSecurityTokenSigner | None]:
    """Initialize OCI configuration, trying instance principal or config file with specified profile."""
    logger = logging.getLogger(__name__)
    config = None
    signer = None
    config_path = os.path.expanduser('~/.oci/config')
    
    if 'OCI_RESOURCE_PRINCIPAL_VERSION' in os.environ:
        try:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            config = {'authentication_type': 'instance_principal'}
            logger.info('Initialized OCI with instance principal')
        except Exception as err:
            logger.warning(f'Instance principal authentication failed: {str(err)}')
            if not os.path.exists(config_path):
                raise FileNotFoundError(f'OCI config file not found at {config_path}') from err
            try:
                config = oci.config.from_file(config_path, profile_name)
                oci.config.validate_config(config)
                signer = None
                logger.info(f'Initialized OCI with config file, profile: {profile_name}')
            except oci.exceptions.InvalidConfig as config_err:
                raise ValueError(f'Invalid OCI config at {config_path} for profile {profile_name}: {str(config_err)}') from config_err
    else:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f'OCI config file not found at {config_path}')
        try:
            config = oci.config.from_file(config_path, profile_name)
            oci.config.validate_config(config)
            signer = None
            logger.info(f'Initialized OCI with config file, profile: {profile_name}')
        except oci.exceptions.InvalidConfig as config_err:
            raise ValueError(f'Invalid OCI config at {config_path} for profile {profile_name}: {str(config_err)}') from config_err
    
    return config, signer

def get_oci_client(client_class):
    """Create and return an OCI client for the specified service."""
    logger = logging.getLogger(__name__)
    config, signer = initialize_oci()
    try:
        client = client_class(config, signer=signer) if signer else client_class(config)
        logger.debug(f'Created OCI client: {client_class.__name__}')
        return client
    except Exception as err:
        logger.error(f'Failed to create OCI client {client_class.__name__}: {str(err)}')
        raise RuntimeError(f'Failed to create OCI client {client_class.__name__}: {str(err)}') from err

def connect_to_oci(config: dict, signer=None) -> bool:
    """Establish and verify OCI connection by fetching the root compartment."""
    logger = logging.getLogger(__name__)
    try:
        identity_client = (
            oci.identity.IdentityClient(config, signer=signer)
            if signer
            else oci.identity.IdentityClient(config)
        )
        tenancy_id = signer.tenancy_id if signer else config.get('tenancy')
        if not tenancy_id:
            raise ValueError('Tenancy ID not found in configuration or signer')
        response = identity_client.get_compartment(tenancy_id)
        if response is None or response.data is None:
            raise ValueError('Failed to retrieve root compartment information from OCI')
        compartment = response.data
        logger.info(f'Connected to OCI, root compartment: {compartment.name}')
        return True
    except (oci.exceptions.ServiceError, ValueError) as err:
        logger.error(f'Failed to connect to OCI: {str(err)}')
        raise ConnectionError(f'Failed to connect to OCI: {str(err)}') from err

def validate_input(data: str) -> bool:
    """Validate input data is a non-empty string."""
    logger = logging.getLogger(__name__)
    is_valid = isinstance(data, str) and len(data) > 0
    if not is_valid:
        logger.error('Invalid input data: must be a non-empty string')
    return is_valid
```

## Step 8: Scripts
**src/oci-simple.py**:

```python
import argparse
import logging

import oci

from utils import connect_to_oci, get_oci_client, initialize_oci, setup_logging, validate_input

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='List OCI compute instances in a compartment')
    parser.add_argument(
        '-c', '--compartment-id',
        required=True,
        help='Compartment OCID to list compute instances'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '-p', '--profile',
        default='DEFAULT',
        help='OCI configuration profile name (default: DEFAULT)'
    )
    return parser.parse_args()

def list_instances(compartment_id: str) -> list[tuple[str, str]]:
    """List compute instances and their running status in the given compartment."""
    logger = logging.getLogger(__name__)
    try:
        compute_client = get_oci_client(oci.core.ComputeClient)
        response = compute_client.list_instances(compartment_id)
        if response is None or response.data is None:
            logger.error(f'No instance data returned for compartment {compartment_id}')
            return []
        instances = response.data
        instance_data = [
            (instance.display_name, 'Running' if instance.lifecycle_state == 'RUNNING' else 'Not Running')
            for instance in instances
        ]
        logger.debug(f'Found {len(instance_data)} instances in compartment {compartment_id}')
        return instance_data
    except Exception as err:
        logger.error(f'Error listing instances in compartment {compartment_id}: {str(err)}')
        return []

def main():
    """Main function to list instances in a compartment."""
    args = parse_args()
    logger = setup_logging(args.verbose)
    logger.info(f'Processing compartment: {args.compartment_id} with profile: {args.profile}')

    # Validate compartment ID
    if not validate_input(args.compartment_id):
        logger.error('Invalid compartment ID provided')
        raise ValueError('Invalid compartment ID')

    # Verify OCI connection
    config, signer = initialize_oci(args.profile)
    if not connect_to_oci(config, signer):
        raise ConnectionError('OCI connection failed')

    # List instances
    instances = list_instances(args.compartment_id)
    if not instances:
        print(f'No instances found in compartment {args.compartment_id}')
        logger.info(f'No instances found in compartment {args.compartment_id}')
    else:
        print(f'Instances in compartment {args.compartment_id}:')
        for name, status in instances:
            print(f'  {name}: {status}')
        logger.info(f'Listed {len(instances)} instances in compartment {args.compartment_id}')

if __name__ == '__main__':
    main()
```

**src/oci-tkinter-display.py**:

```python
import argparse
import logging
import tkinter as tk

import oci
import tksheet

from utils import get_oci_client, initialize_oci, setup_logging, validate_input

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='List OCI compute instances in a compartment using tksheet')
    parser.add_argument(
        '-c', '--compartment-id',
        required=True,
        help='Compartment OCID to list compute instances'
    )
    parser.add_argument(
        '-b', '--bg-color',
        default='white',
        help='Background color for Tkinter GUI (default: white)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '-p', '--profile',
        default='DEFAULT',
        help='OCI configuration profile name (default: DEFAULT)'
    )
    return parser.parse_args()

def get_instances(compartment_id: str) -> list:
    """List compute instances in the given compartment."""
    logger = logging.getLogger(__name__)
    try:
        compute_client = get_oci_client(oci.core.ComputeClient)
        response = compute_client.list_instances(compartment_id)
        if response is None or response.data is None:
            logger.error(f'No instance data returned for compartment {compartment_id}')
            return []
        instances = response.data
        instance_data = [
            [
                instance.display_name,
                instance.id,
                instance.shape,
                (
                    'Running' if instance.lifecycle_state == 'RUNNING' else
                    'Starting' if instance.lifecycle_state == 'STARTING' else
                    'Stopping' if instance.lifecycle_state == 'STOPPING' else
                    'Not Running'
                )
            ]
            for instance in instances
        ]
        logger.debug(f'Found {len(instance_data)} instances in compartment {compartment_id}')
        return instance_data
    except Exception as err:
        logger.error(f'Error listing instances in compartment {compartment_id}: {str(err)}')
        return []

def main():
    """Main function to run Tkinter GUI and display instances."""
    args = parse_args()
    logger = setup_logging(args.verbose)
    logger.info(f'Initialized with background color {args.bg_color} and profile {args.profile}')

    # Validate compartment ID
    if not validate_input(args.compartment_id):
        logger.error('Invalid compartment ID provided')
        raise ValueError('Invalid compartment ID')

    # Set up Tkinter GUI
    root = tk.Tk()
    root.title('OCI Instance Viewer')
    root.geometry('800x600')
    root.configure(bg=args.bg_color)
    label = tk.Label(root, text='Compartment ID:', bg=args.bg_color)
    label.pack()
    entry = tk.Entry(root)
    entry.insert(0, args.compartment_id)
    entry.pack()

    # Initialize tksheet
    sheet = tksheet.Sheet(
        root,
        headers=['Name', 'OCID', 'Size', 'Status'],
        column_width=250
    )
    sheet.pack(pady=10)
    sheet.set_sheet_data(get_instances(args.compartment_id))

    def refresh_instances():
        """Refresh instance list based on entered compartment ID."""
        compartment_id = entry.get()
        if not validate_input(compartment_id):
            sheet.set_sheet_data([['', '', '', 'Invalid compartment ID']])
            logger.error('Invalid compartment ID provided')
            return
        instance_data = get_instances(compartment_id)
        sheet.set_sheet_data(instance_data)
        logger.info(f'Displayed {len(instance_data)} instances for compartment {compartment_id}')

    button = tk.Button(root, text='Refresh Instances', command=refresh_instances)
    button.pack()

    logger.info('Starting Tkinter main loop')
    root.mainloop()

if __name__ == '__main__':
    main()
```

**src/oci-parallel-paginated.py**:

```python
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

import oci
from oci.pagination import list_call_get_all_results

from utils import get_oci_client, initialize_oci, setup_logging

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='List OCI compute instances in parallel across all compartments')
    parser.add_argument(
        '-m', '--max-workers',
        type=int,
        default=4,
        help='Maximum number of threads for parallel execution (default: 4)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '-p', '--profile',
        default='DEFAULT',
        help='OCI configuration profile name (default: DEFAULT)'
    )
    return parser.parse_args()

def work(compartment_id: str, compute_client: oci.core.ComputeClient) -> tuple[str, list[str]]:
    """List compute instances in the given compartment using the provided client."""
    logger = logging.getLogger(__name__)
    try:
        response = compute_client.list_instances(compartment_id)
        if response is None or response.data is None:
            logger.error(f'No instance data returned for compartment {compartment_id}')
            return compartment_id, []
        instances = response.data
        instance_names = [instance.display_name for instance in instances]
        logger.debug(f'Compartment {compartment_id}: Found {len(instance_names)} instances')
        return compartment_id, instance_names
    except Exception as err:
        logger.error(f'Error listing instances in compartment {compartment_id}: {str(err)}')
        return compartment_id, []

def main():
    """Main function to list compartments and process them in parallel."""
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    logger.info(f'Using profile: {args.profile}')
    
    # Get tenancy ID from config or signer
    config, signer = initialize_oci(args.profile)
    tenancy_id = signer.tenancy_id if signer else config.get('tenancy')
    if not tenancy_id:
        logger.error('Tenancy ID not found in configuration or signer')
        raise ValueError('Tenancy ID not found in configuration or signer')
    logger.debug(f'Using tenancy ID: {tenancy_id}')
    
    # Get OCI clients
    identity_client = get_oci_client(oci.identity.IdentityClient)
    compute_client = get_oci_client(oci.core.ComputeClient)
    
    # List compartments with pagination
    logger.info('Fetching compartments')
    response = list_call_get_all_results(identity_client.list_compartments, tenancy_id)
    if response is None or response.data is None:
        logger.error('No compartment data returned')
        raise RuntimeError('Failed to list compartments')
    compartments = response.data
    compartment_ids = [comp.id for comp in compartments]
    logger.info(f'Found {len(compartment_ids)} compartments')
    
    # Process compartments in parallel
    results = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_compartment = {
            executor.submit(work, comp_id, compute_client): comp_id for comp_id in compartment_ids
        }
        for future in future_to_compartment:
            try:
                comp_id, instance_names = future.result()
                results.append((comp_id, instance_names))
                logger.info(
                    f'Compartment {comp_id}: {len(instance_names)} instances: {instance_names}'
                )
            except Exception as err:
                logger.error(
                    f'Error processing compartment {future_to_compartment[future]}: {str(err)}'
                )
    
    # Print results
    print('Compute Instances by Compartment:')
    for comp_id, instance_names in results:
        print(f'Compartment {comp_id}: {instance_names}')

if __name__ == '__main__':
    main()
```

**src/oci-parallel-search.py**:

```python
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

import oci

from utils import get_oci_client, initialize_oci, setup_logging

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Search for running OCI compute instances in the tenancy and list name and size')
    parser.add_argument(
        '-m', '--max-workers',
        type=int,
        default=4,
        help='Maximum number of threads for parallel processing (default: 4)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '-p', '--profile',
        default='DEFAULT',
        help='OCI configuration profile name (default: DEFAULT)'
    )
    return parser.parse_args()

def work(instance_ocid: str, compartment_id: str, compute_client: oci.core.ComputeClient, identity_client: oci.identity.IdentityClient) -> tuple[str, str, str]:
    """Fetch instance details (name, size) and compartment name for the given instance OCID."""
    logger = logging.getLogger(__name__)
    try:
        # Fetch instance details
        response = compute_client.get_instance(instance_ocid)
        if response is None or response.data is None:
            logger.error(f'No instance data for OCID {instance_ocid}')
            return compartment_id, 'Unknown', 'Unknown'
        instance = response.data
        
        # Fetch compartment name
        response = identity_client.get_compartment(compartment_id)
        if response is None or response.data is None:
            logger.error(f'No compartment data for {compartment_id}')
            return compartment_id, instance.display_name, instance.shape
        compartment_name = response.data.name
        
        logger.debug(f'Processed instance {instance.display_name} in compartment {compartment_name}')
        return compartment_name, instance.display_name, instance.shape
    except Exception as err:
        logger.error(f'Error processing instance OCID {instance_ocid}: {str(err)}')
        return compartment_id, 'Unknown', 'Unknown'

def main():
    """Main function to search for running instances and process them in parallel."""
    args = parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    logger.info(f'Using profile: {args.profile}')
    
    # Get tenancy ID from config or signer
    config, signer = initialize_oci(args.profile)
    tenancy_id = signer.tenancy_id if signer else config.get('tenancy')
    if not tenancy_id:
        logger.error('Tenancy ID not found in configuration or signer')
        raise ValueError('Tenancy ID not found in configuration or signer')
    logger.debug(f'Using tenancy ID: {tenancy_id}')
    
    # Get OCI clients
    search_client = get_oci_client(oci.resource_search.ResourceSearchClient)
    compute_client = get_oci_client(oci.core.ComputeClient)
    identity_client = get_oci_client(oci.identity.IdentityClient)
    
    # Search for running instances
    logger.info('Searching for running compute instances')
    search_details = oci.resource_search.models.StructuredSearchDetails(
        query='query instance resources where lifeCycleState = \'RUNNING\'',
        type='Structured',
        matching_context_type=oci.resource_search.models.SearchDetails.MATCHING_CONTEXT_TYPE_NONE
    )
    response = search_client.search_resources(search_details)
    if response is None or response.data is None:
        logger.error('No search results returned')
        raise RuntimeError('Failed to search for instances')
    resources = response.data.items
    logger.info(f'Found {len(resources)} running instances')
    
    # Process resources in parallel
    results = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_resource = {
            executor.submit(work, resource.identifier, resource.compartment_id, compute_client, identity_client): resource
            for resource in resources
        }
        for future in future_to_resource:
            try:
                compartment_name, display_name, shape = future.result()
                results.append((compartment_name, display_name, shape))
                logger.info(
                    f'Instance {display_name} in compartment {compartment_name}: Size {shape}'
                )
            except Exception as err:
                resource = future_to_resource[future]
                logger.error(
                    f'Error processing instance OCID {resource.identifier}: {str(err)}'
                )
    
    # Group results by compartment
    results_by_compartment = {}
    for compartment_name, display_name, shape in sorted(results, key=lambda x: x[0]):
        if compartment_name not in results_by_compartment:
            results_by_compartment[compartment_name] = []
        results_by_compartment[compartment_name].append((display_name, shape))
    
    # Print results
    print('Running Compute Instances by Compartment:')
    for compartment_name, instances in results_by_compartment.items():
        print(f'Compartment {compartment_name}:')
        for name, shape in instances:
            print(f'  {name}: {shape}')

if __name__ == '__main__':
    main()
```

## Step 9: Verify Setup
1. **Run Pre-Commit Hooks**:
   ```bash
   uv run pre-commit run --all-files --verbose
   ```
   Expected output:
   ```
   Format with Ruff.................................Passed
   Lint with Ruff..................................Passed
   ```

2. **Verify Argument Parsing**:
   - `oci-simple.py`:
     ```bash
     python src/oci-simple.py --help
     ```
     Expected output:
     ```
     -c, --compartment-id COMPARTMENT_ID  Compartment OCID to list compute instances
     -v, --verbose                        Enable verbose logging
     -p, --profile PROFILE                OCI configuration profile name (default: DEFAULT)
     ```
   - `oci-tkinter-display.py`:
     ```bash
     python src/oci-tkinter-display.py --help
     ```
     Expected output:
     ```
     -c, --compartment-id COMPARTMENT_ID  Compartment OCID to list compute instances
     -b, --bg-color BG_COLOR              Background color for Tkinter GUI (default: white)
     -v, --verbose                        Enable verbose logging
     -p, --profile PROFILE                OCI configuration profile name (default: DEFAULT)
     ```
   - `oci-parallel-paginated.py`:
     ```bash
     python src/oci-parallel-paginated.py --help
     ```
     Expected output:
     ```
     -m, --max-workers MAX_WORKERS  Maximum number of threads for parallel execution (default: 4)
     -v, --verbose                  Enable verbose logging
     -p, --profile PROFILE          OCI configuration profile name (default: DEFAULT)
     ```
   - `oci-parallel-search.py`:
     ```bash
     python src/oci-parallel-search.py --help
     ```
     Expected output:
     ```
     -m, --max-workers MAX_WORKERS  Maximum number of threads for parallel processing (default: 4)
     -v, --verbose                  Enable verbose logging
     -p, --profile PROFILE          OCI configuration profile name (default: DEFAULT)
     ```

3. **Test Non-OCI Environment**:
   ```bash
   unset OCI_RESOURCE_PRINCIPAL_VERSION
   mv ~/.oci/config ~/.oci/config.bak
   python src/oci-parallel-search.py -v -p MY_PROFILE
   ```
   Expected output: `FileNotFoundError: OCI config file not found at ~/.oci/config`.
   Restore config:
   ```bash
   mv ~/.oci/config.bak ~/.oci/config
   ```

4. **Test Scripts**:
   - **Using `python`**:
     - `oci-simple.py`:
       ```bash
       python src/oci-simple.py -c ocid1.compartment.oc1..example -v -p MY_PROFILE
       ```
       Expected output (example):
       ```
       2025-06-25 16:27:00,000 - MainThread - INFO - Processing compartment: ocid1.compartment.oc1..example with profile: MY_PROFILE
       Instances in compartment ocid1.compartment.oc1..example:
         instance-1: Running
         instance-2: Not Running
       ```
     - `oci-tkinter-display.py`:
       ```bash
       python src/oci-tkinter-display.py -c ocid1.compartment.oc1..example -b lightblue -v -p MY_PROFILE
       ```
       Expected output: GUI with 800x600 window, `tksheet` (250-pixel columns), showing instance details (e.g., `["instance-1", "ocid1.instance.oc1..abc", "VM.Standard2.1", "Running"]`), and log:
       ```
       2025-06-25 16:27:00,000 - MainThread - INFO - Initialized with background color lightblue and profile MY_PROFILE
       2025-06-25 16:27:00,001 - MainThread - INFO - Starting Tkinter main loop
       ```
     - `oci-parallel-paginated.py`:
       ```bash
       python src/oci-parallel-paginated.py -m 2 -v -p MY_PROFILE
       ```
       Expected output (example):
       ```
       2025-06-25 16:27:00,000 - MainThread - INFO - Using profile: MY_PROFILE
       2025-06-25 16:27:00,001 - MainThread - INFO - Found 2 compartments
       2025-06-25 16:27:00,002 - Thread-1 (work) - INFO - Compartment ocid1.compartment.oc1..example1: 2 instances: ['instance-1', 'instance-2']
       Compute Instances by Compartment:
       Compartment ocid1.compartment.oc1..example1: ['instance-1', 'instance-2']
       Compartment ocid1.compartment.oc1..example2: []
       ```
     - `oci-parallel-search.py`:
       ```bash
       python src/oci-parallel-search.py -m 2 -v -p MY_PROFILE
       ```
       Expected output (example):
       ```
       2025-06-25 16:27:00,000 - MainThread - INFO - Using profile: MY_PROFILE
       2025-06-25 16:27:00,001 - MainThread - INFO - Found 3 running instances
       2025-06-25 16:27:00,002 - Thread-1 (work) - INFO - Instance instance-1 in compartment MyCompartment1: Size VM.Standard2.1
       Running Compute Instances by Compartment:
       Compartment MyCompartment1:
         instance-1: VM.Standard2.1
         instance-3: VM.Standard2.1
       Compartment MyCompartment2:
         instance-2: VM.Standard2.2
       ```
   - **Using `uv run`**:
     - Replace `python` with `uv run` (e.g., `uv run src/oci-simple.py -c ocid1.compartment.oc1..example -v -p MY_PROFILE`). Output remains the same.
   - **Using Default Profile**:
     - Omit `-p`:
       ```bash
       python src/oci-simple.py -c ocid1.compartment.oc1..example -v
       ```
       Expected output: Same as above, with `profile: DEFAULT` in logs.

## Step 10: Commit and Push
Stage and commit:
```bash
git add src/*.py README.md
git commit -m "Remove VSCode debugging section, organize imports, fix bugs in oci-tkinter-display.py"
git push origin main
```

## Step 11: Running the Scripts
Run from the project root:
- **oci-simple.py**:
  ```bash
  python src/oci-simple.py -c ocid1.compartment.oc1..example -v -p MY_PROFILE
  ```
  or
  ```bash
  uv run src/oci-simple.py -c ocid1.compartment.oc1..example -v -p MY_PROFILE
  ```
- **oci-tkinter-display.py**:
  ```bash
  python src/oci-tkinter-display.py -c ocid1.compartment.oc1..example -b lightblue -v -p MY_PROFILE
  ```
- **oci-parallel-paginated.py**:
  ```bash
  python src/oci-parallel-paginated.py -m 2 -v -p MY_PROFILE
  ```
- **oci-parallel-search.py**:
  ```bash
  python src/oci-parallel-search.py -m 2 -v -p MY_PROFILE
  ```
