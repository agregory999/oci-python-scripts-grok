import argparse
import logging
from concurrent.futures import ThreadPoolExecutor

import oci

from utils import get_oci_client, initialize_oci, setup_logging


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Search for running OCI compute instances in the tenancy and list name and size'
    )
    parser.add_argument(
        '-m',
        '--max-workers',
        type=int,
        default=4,
        help='Maximum number of threads for parallel processing (default: 4)',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Enable verbose logging'
    )
    parser.add_argument(
        '-p',
        '--profile',
        default='DEFAULT',
        help='OCI configuration profile name (default: DEFAULT)',
    )
    return parser.parse_args()


def work(
    instance_ocid: str,
    compartment_id: str,
    compute_client: oci.core.ComputeClient,
    identity_client: oci.identity.IdentityClient,
) -> tuple[str, str, str]:
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

        logger.debug(
            f'Processed instance {instance.display_name} in compartment {compartment_name}'
        )
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
        raise RuntimeError('Tenancy ID not found in configuration or signer')
    logger.debug(f'Using tenancy ID: {tenancy_id}')

    # Get OCI clients
    search_client = get_oci_client(oci.resource_search.ResourceSearchClient)
    compute_client = get_oci_client(oci.core.ComputeClient)
    identity_client = get_oci_client(oci.identity.IdentityClient)

    # Search for running instances
    logger.info('Searching for running compute instances')
    search_details = oci.resource_search.models.StructuredSearchDetails(
        query="query instance resources where lifeCycleState = 'RUNNING'",
        type='Structured',
        matching_context_type=oci.resource_search.models.SearchDetails.MATCHING_CONTEXT_TYPE_NONE,
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
            executor.submit(
                work,
                resource.identifier,
                resource.compartment_id,
                compute_client,
                identity_client,
            ): resource
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
