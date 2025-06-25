import argparse
import datetime
from pathlib import Path

from oci.exceptions import ServiceError
from oci.log_analytics import LogAnalyticsClient
from oci.log_analytics.models import ExportDetails, TimeRange

from utils import (
    connect_to_oci,
    get_oci_client,
    initialize_oci,
    setup_logging,
    validate_input,
)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Call OCI Logging Analytics Extract')
    parser.add_argument(
        '-c', '--compartment-ocid', required=True, help='Target compartment OCID'
    )
    parser.add_argument(
        '-s',
        '--start-time',
        default=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        help='Query start time (ISO format: YYYY-MM-DDTHH:MM:SS)',
    )
    parser.add_argument(
        '-e',
        '--end-time',
        default=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        help='Query end time (ISO format: YYYY-MM-DDTHH:MM:SS)',
    )
    parser.add_argument(
        '--query', required=True, help='OCI LA query string - verify in UI first'
    )
    parser.add_argument(
        '-ns', '--namespace', required=True, help='OCI Log Analytics namespace'
    )
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    return parser.parse_args()


def process(data: str) -> str:
    """Process input data to uppercase after verifying OCI connection."""
    config, signer = initialize_oci()
    if not connect_to_oci(config, signer):
        raise ConnectionError('OCI connection failed')
    if not validate_input(data):
        raise ValueError('Invalid input data')
    return data.upper()


def main():
    """Main function to process input and output to console."""
    args = parse_args()
    logger = setup_logging(args.verbose)
    logger.debug(f'Args used: {args}')
    logger.info(
        f'Processing Query: {args.query} for start time {args.start_time} and end time {args.end_time}'
    )

    config, signer = initialize_oci()
    if not connect_to_oci(config, signer):
        raise ConnectionError('OCI connection failed')
    logging_analytics_client: LogAnalyticsClient = get_oci_client(LogAnalyticsClient)

    try:
        # Actual implementation
        logger.info(
            f'Starting extraction from {args.start_time} to {args.end_time} with compartment {args.compartment_ocid}'
        )

        # Create Export Details
        export_details = ExportDetails(
            compartment_id=args.compartment_ocid,
            sub_system='LOG',
            query_string=args.query,
            output_format='CSV',
            time_filter=TimeRange(
                time_start=datetime.datetime.fromisoformat(args.start_time),
                time_end=datetime.datetime.fromisoformat(args.end_time),
                time_zone='UTC',
            ),
            max_total_count=1_000_000,
            should_include_columns=True,
        )
        logger.debug(f'Input: {export_details}')

        query_start = datetime.datetime.now()

        logger.debug(f'LA Client: {logging_analytics_client}')

        response = logging_analytics_client.export_query_result(
            namespace_name=args.namespace, export_details=export_details
        )

        query_duration = datetime.datetime.now() - query_start
        logger.info(f'Query completed in {query_duration}')

        # Write to file
        output_path = Path('./test.csv')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        write_start = datetime.datetime.now()
        with output_path.open('wb') as f:
            f.write(response.data.content)  # type: ignore

        write_duration = datetime.datetime.now() - write_start
        file_size = output_path.stat().st_size

        logger.info(
            f'Data written to {output_path} '
            f'(Size: {file_size:,} bytes, Write time: {write_duration})'
        )

    except ServiceError as ex:
        logger.error(
            f'OCI Service Error - Service: {ex.target_service}, '
            f'Operation: {ex.operation_name}, Code: {ex.code}'
        )
        logger.debug(f'Full exception: {ex}')
        raise
    except Exception as ex:
        logger.error(f'Unexpected error during extraction: {ex}')
        raise

    logger.info('Complete')


if __name__ == '__main__':
    main()
