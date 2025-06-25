import argparse
import logging
import tkinter as tk

import oci
import tksheet

from utils import get_oci_client, setup_logging, validate_input


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='List OCI compute instances in a compartment using tksheet'
    )
    parser.add_argument(
        '-c',
        '--compartment-id',
        required=True,
        help='Compartment OCID to list compute instances',
    )
    parser.add_argument(
        '-b',
        '--bg-color',
        default='white',
        help='Background color for Tkinter GUI (default: white)',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Enable verbose logging'
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
                    'Running'
                    if instance.lifecycle_state == 'RUNNING'
                    else 'Starting'
                    if instance.lifecycle_state == 'STARTING'
                    else 'Stopping'
                    if instance.lifecycle_state == 'STOPPING'
                    else 'Not Running'
                ),
            ]
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
    """Main function to run Tkinter GUI and display instances."""
    args = parse_args()
    logger = setup_logging(args.verbose)
    logger.info(f'Initialized with background color {args.bg_color}')

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
        root, headers=['Name', 'OCID', 'Size', 'Status'], column_width=250
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
        logger.info(
            f'Displayed {len(instance_data)} instances for compartment {compartment_id}'
        )

    button = tk.Button(root, text='Refresh Instances', command=refresh_instances)
    button.pack()

    logger.info('Starting Tkinter main loop')
    root.mainloop()


if __name__ == '__main__':
    main()
