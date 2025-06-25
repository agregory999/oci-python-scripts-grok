import argparse
import datetime
from pathlib import Path

from oci.exceptions import ServiceError
from oci.log_analytics import LogAnalyticsClient
from oci.log_analytics.models import ExportDetails, TimeRange

from oci_python_scripts_grok.templates.base import BaseProcessor


class LoggingAnalyticsExtract(BaseProcessor):
    """Processor that converts text to uppercase using OCI."""

    def __init__(self):
        super().__init__()
        self.args = self._parse_args().parse_args()
        self._setup_logging()  # Re-setup logging with parsed args
        self._initialize_oci()
        self._create_client()
        self.logger.info('Initialized LoggingAnalyticsExtract')

    def _create_client(self):
        """Establish and verify OCI connection."""
        try:
            # Use signer for instance principal or config for file-based auth
            self.logging_analytics_client = (
                LogAnalyticsClient(self.config, signer=self.signer)
                if self.signer
                else LogAnalyticsClient(self.config)
            )

            return True
        except ServiceError as err:
            self.logger.error(f'Failed to connect to OCI: {str(err)}')
            raise ConnectionError(f'Failed to connect to OCI: {str(err)}') from err

    def _parse_args(self):
        """Parse command-line arguments, inheriting from base parser."""
        parser = argparse.ArgumentParser(
            description='Process text to uppercase with OCI',
            parents=[super()._parse_args()],
        )
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
        # Additional Args required
        parser.add_argument(
            '--query', required=True, help='OCI LA query string - verify in UI first'
        )
        parser.add_argument(
            '-ns', '--namespace', required=True, help='OCI Log Analytics namespace'
        )

        return parser

    def process(self, data: str) -> str:
        """Process input data to uppercase after verifying OCI connection."""
        if not self.connect_to_oci():
            raise ConnectionError('OCI connection failed')
        if not self.validate(data):
            raise ValueError('Invalid query data')

        # Actual implementation
        self.logger.info(
            f'Starting extraction from {self.args.start_time} to {self.args.end_time} with compartment {self.args.compartment_ocid}'
        )

        # Create Export Details
        export_details = ExportDetails(
            compartment_id=self.args.compartment_ocid,
            sub_system='LOG',
            query_string=self.args.query,
            output_format='CSV',
            time_filter=TimeRange(
                time_start=datetime.datetime.fromisoformat(self.args.start_time),
                time_end=datetime.datetime.fromisoformat(self.args.end_time),
                time_zone='UTC',
            ),
            max_total_count=1_000_000,
            should_include_columns=True,
        )
        self.logger.debug(f'Input: {export_details}')
        try:
            query_start = datetime.datetime.now()

            response = self.logging_analytics_client.export_query_result(
                namespace_name=self.args.namespace, export_details=export_details
            )

            query_duration = datetime.datetime.now() - query_start
            self.logger.info(f'Query completed in {query_duration}')

            # Write to file
            output_path = Path('./test.csv')
            output_path.parent.mkdir(parents=True, exist_ok=True)

            write_start = datetime.datetime.now()
            with output_path.open('wb') as f:
                f.write(response.data.content)  # type: ignore

            write_duration = datetime.datetime.now() - write_start
            file_size = output_path.stat().st_size

            self.logger.info(
                f'Data written to {output_path} '
                f'(Size: {file_size:,} bytes, Write time: {write_duration})'
            )

        except ServiceError as ex:
            self.logger.error(
                f'OCI Service Error - Service: {ex.target_service}, '
                f'Operation: {ex.operation_name}, Code: {ex.code}'
            )
            self.logger.debug(f'Full exception: {ex}')
            raise
        except Exception as ex:
            self.logger.error(f'Unexpected error during extraction: {ex}')
            raise

        return 'complete'

    def run(self):
        """Process the input string and output to console."""
        self.logger.info(f'Start Time: {self.args.start_time}')
        result = self.process(self.args.query)
        print(f'Result: {result}')
        self.logger.info(f'Processed Query: {self.args.query} -> {result}')


if __name__ == '__main__':
    processor = LoggingAnalyticsExtract()
    processor.run()
