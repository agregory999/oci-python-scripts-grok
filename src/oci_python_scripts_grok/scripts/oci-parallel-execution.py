import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

import oci
from oci.pagination import list_call_get_all_results

from oci_python_scripts_grok.utils import get_oci_client, initialize_oci, setup_logging


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='List OCI compute instances in parallel across all compartments'
    )
    parser.add_argument(
        '-m',
        '--max-workers',
        type=int,
        default=4,
        help='Maximum number of threads for parallel execution (default: 4)',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Enable verbose logging'
    )
    return parser.parse_args()


def work(
    compartment_id: str, compute_client: oci.core.ComputeClient
) -> tuple[str, list[str]]:
    """List compute instances in the given compartment using the provided client."""
    logger = logging.getLogger(__name__)
    try:
        response = compute_client.list_instances(compartment_id)
        if response is None or response.data is None:
            logger.error(f'No instance data returned for compartment {compartment_id}')
            return compartment_id, []
        instances = response.data
        instance_names = [instance.display_name for instance in instances]
        logger.debug(
            f'Compartment {compartment_id}: Found {len(instance_names)} instances'
        )
        return compartment_id, instance_names
    except Exception as err:
        logger.error(
            f'Error listing instances in compartment {compartment_id}: {str(err)}'
        )
        return compartment_id, []


def main():
    """Main function to list compartments and process them in parallel."""
    args = parse_args()
    setup_logging(args.verbose)

    # Get tenancy ID from config or signer
    config, signer = initialize_oci()
    tenancy_id = signer.tenancy_id if signer else config.get('tenancy')
    if not tenancy_id:
        raise ValueError('Tenancy ID not found in OCI configuration or signer')
    logging.getLogger(__name__).debug(f'Using tenancy ID: {tenancy_id}')

    # Get OCI clients
    identity_client = get_oci_client(oci.identity.IdentityClient)
    compute_client = get_oci_client(oci.core.ComputeClient)

    # List compartments with pagination
    logging.getLogger(__name__).info('Fetching compartments')
    response = list_call_get_all_results(identity_client.list_compartments, tenancy_id)
    if response is None or response.data is None:
        logging.getLogger(__name__).error('No compartment data returned')
        raise RuntimeError('Failed to list compartments')
    compartments = response.data
    compartment_ids = [comp.id for comp in compartments]
    logging.getLogger(__name__).info(f'Found {len(compartment_ids)} compartments')

    # Process compartments in parallel
    results = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        future_to_compartment = {
            executor.submit(work, comp_id, compute_client): comp_id
            for comp_id in compartment_ids
        }
        for future in future_to_compartment:
            try:
                comp_id, instance_names = future.result()
                results.append((comp_id, instance_names))
                logging.getLogger(__name__).info(
                    f'Compartment {comp_id}: {len(instance_names)} instances: {instance_names}'
                )
            except Exception as err:
                logging.getLogger(__name__).error(
                    f'Error processing compartment {future_to_compartment[future]}: {str(err)}'
                )

    # Print results
    print('Compute Instances by Compartment:')
    for comp_id, instance_names in results:
        print(f'Compartment {comp_id}: {instance_names}')


if __name__ == '__main__':
    main()
