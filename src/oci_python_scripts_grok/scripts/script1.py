import argparse

from oci_python_scripts_grok.templates.base import BaseProcessor


class UpperCaseProcessor(BaseProcessor):
    """Processor that converts text to uppercase using OCI."""

    def __init__(self):
        super().__init__()
        self.args = self._parse_args().parse_args()
        self._setup_logging()  # Re-setup logging with parsed args
        self._initialize_oci()
        self.logger.info(
            f'Initialized UpperCaseProcessor (font-size {self.args.font_size} ignored)'
        )

    def _parse_args(self):
        """Parse command-line arguments, inheriting from base parser."""
        parser = argparse.ArgumentParser(
            description='Process text to uppercase with OCI',
            parents=[super()._parse_args()],
        )
        parser.add_argument('--input', required=True, help='Input string to process')
        parser.add_argument(
            '--font-size',
            type=int,
            default=12,
            help='Font size (ignored, retained for compatibility)',
        )
        return parser

    def process(self, data: str) -> str:
        """Process input data to uppercase after verifying OCI connection."""
        if not self.connect_to_oci():
            raise ConnectionError('OCI connection failed')
        if not self.validate(data):
            raise ValueError('Invalid input data')
        return data.upper()

    def run(self):
        """Process the input string and output to console."""
        self.logger.info(f'Processing input: {self.args.input}')
        result = self.process(self.args.input)
        print(f'Result: {result}')
        self.logger.info(f'Processed input: {self.args.input} -> {result}')


if __name__ == '__main__':
    processor = UpperCaseProcessor()
    processor.run()
