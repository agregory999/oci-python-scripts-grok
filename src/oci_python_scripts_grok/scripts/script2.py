import argparse
import tkinter as tk

import tksheet

from oci_python_scripts_grok.templates.base import BaseProcessor


class ReverseProcessor(BaseProcessor):
    """Processor that reverses text and displays in tksheet."""

    def __init__(self):
        super().__init__()
        self.args = self._parse_args().parse_args()
        self._setup_logging()  # Re-setup logging with parsed args
        self._initialize_oci()
        self.root = tk.Tk()
        self.root.title('Reverse Processor')
        self.root.configure(bg=self.args.bg_color)
        self.label = tk.Label(self.root, text='Enter text:', bg=self.args.bg_color)
        self.label.pack()
        self.entry = tk.Entry(self.root)
        self.entry.insert(0, self.args.input)
        self.entry.pack()
        self.button = tk.Button(
            self.root, text='Process', command=self._process_and_display
        )
        self.button.pack()
        # Initialize tksheet
        self.sheet = tksheet.Sheet(self.root, headers=['Input', 'Result'])
        self.sheet.pack(pady=10)
        self.sheet.set_sheet_data([[self.args.input, '']])
        self.logger.info(
            f'Initialized ReverseProcessor with background color {self.args.bg_color}'
        )

    def _parse_args(self):
        """Parse command-line arguments, inheriting from base parser."""
        parser = argparse.ArgumentParser(
            description='Process text to reverse with tksheet and OCI',
            parents=[super()._parse_args()],
        )
        parser.add_argument('--input', required=True, help='Input string to process')
        parser.add_argument(
            '--bg-color',
            default='white',
            help='Background color for Tkinter GUI (default: white)',
        )
        return parser

    def _process_and_display(self):
        """Process input from entry and display in tksheet."""
        data = self.entry.get()
        if not self.validate(data):
            self.sheet.set_sheet_data([[data, 'Invalid input']])
            self.logger.error('Invalid input provided')
            return
        result = self.process(data)
        self.sheet.set_sheet_data([[data, result]])
        self.logger.info(f'Processed input: {data} -> {result}')

    def process(self, data: str) -> str:
        """Process input data to reverse after verifying OCI connection."""
        if not self.connect_to_oci():
            raise ConnectionError('OCI connection failed')
        if not self.validate(data):
            raise ValueError('Invalid input data')
        return data[::-1]

    def run(self):
        """Start the Tkinter main loop."""
        self.logger.info('Starting Tkinter main loop for ReverseProcessor')
        self.root.mainloop()


if __name__ == '__main__':
    processor = ReverseProcessor()
    processor.run()
