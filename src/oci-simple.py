import argparse
import logging

import oci

from utils import (
    connect_to_oci,
    get_oci_client,
    initialize_oci,
    setup_logging,
    validate_input,
)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='List OCI compute instances in a compartment'
    )
    parser.add_argument(
        '-c',
        '--compartment-id',
        required=True,
        help='Compartment OCID to list compute instances',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Enable verbose logging'
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
            (
                instance.display_name,
                'Running' if instance.lifecycle_state == 'RUNNING' else 'Not Running',
            )
            for instance in instances
        ]
        logger.debug(
            f'Found {len(instance_data)} instances in compartment {compartment_id}'
        )
        return instance_data
    except Exception as err:
        logger.error(
            f'Error listing instances in compartment {compartment_id}: {str(err)}'
        )
        return []


def main():
    """Main function to list instances in a compartment."""
    args = parse_args()
    logger = setup_logging(args.verbose)
    logger.info(f'Processing compartment: {args.compartment_id}')

    # Validate compartment ID
    if not validate_input(args.compartment_id):
        logger.error('Invalid compartment ID provided')
        raise ValueError('Invalid compartment ID')

    # Verify OCI connection
    config, signer = initialize_oci()
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
        logger.info(
            f'Listed {len(instances)} instances in compartment {args.compartment_id}'
        )


if __name__ == '__main__':
    main()
