import argparse
import logging
import os
from abc import ABC, abstractmethod

import oci


class BaseProcessor(ABC):
    """Abstract base class for data processors with OCI connection and argparse."""

    def __init__(self):
        """Initialize with OCI configuration and parsed arguments."""
        self.args = None  # Set in subclasses after parsing
        self._setup_logging()
        self.signer = None
        self.config = None

    def _parse_args(self):
        """Create and return argument parser for base arguments."""
        parser = argparse.ArgumentParser(
            description='Base processor with OCI connection', add_help=False
        )
        parser.add_argument(
            '--verbose', action='store_true', help='Enable verbose logging'
        )
        parser.add_argument(
            '--config-file',
            default='~/.oci/config',
            help='Path to OCI config file (default: ~/.oci/config)',
        )
        parser.add_argument(
            '--profile',
            default='DEFAULT',
            help='OCI config profile name (default: DEFAULT)',
        )
        return parser

    def _setup_logging(self):
        """Set up logging based on verbose flag."""
        # Default to INFO until args are parsed in subclasses
        level = logging.DEBUG if getattr(self.args, 'verbose', False) else logging.INFO
        logging.basicConfig(
            level=level, format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_oci(self):
        """Initialize OCI configuration after args are parsed."""
        if 'OCI_RESOURCE_PRINCIPAL_VERSION' in os.environ:
            try:
                self.signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
                self.config = {'authentication_type': 'instance_principal'}
            except Exception as err:
                self.logger.warning(
                    f'Instance principal authentication failed: {str(err)}'
                )
                self._fallback_to_config_file(err)
        else:
            self._fallback_to_config_file(None)

    def _fallback_to_config_file(self, err):
        """Fallback to OCI config file authentication."""
        config_path = os.path.expanduser(self.args.config_file)  # type: ignore
        if not os.path.exists(config_path):
            if err:
                raise FileNotFoundError(
                    f'OCI config file not found at {config_path}'
                ) from err
            raise FileNotFoundError(f'OCI config file not found at {config_path}')
        self.config = oci.config.from_file(config_path, self.args.profile)  # type: ignore
        oci.config.validate_config(self.config)
        self.signer = None

    def connect_to_oci(self):
        """Establish and verify OCI connection."""
        try:
            # Use signer for instance principal or config for file-based auth
            identity_client = (
                oci.identity.IdentityClient(self.config, signer=self.signer)
                if self.signer
                else oci.identity.IdentityClient(self.config)
            )
            # Test connection by fetching user info
            # Original (AI)
            # user = identity_client.get_user(self.config.get("user")).data # type: ignore
            # self.logger.info(f"Connected as user: {user.name}")

            # My Change - just get the root compartment name
            comp = identity_client.get_compartment(self.config.get('tenancy')).data  # type: ignore
            self.logger.info(
                f'Successfully connected to OCI - root compartment: {comp.name}'
            )
            return True
        except oci.exceptions.ServiceError as err:
            self.logger.error(f'Failed to connect to OCI: {str(err)}')
            raise ConnectionError(f'Failed to connect to OCI: {str(err)}') from err

    @abstractmethod
    def process(self, data: str) -> str:
        """Process input data and return result."""
        pass

    def validate(self, data: str) -> bool:
        """Validate input data."""
        is_valid = isinstance(data, str) and len(data) > 0
        if not is_valid:
            self.logger.error('Invalid input data: must be a non-empty string')
        return is_valid
