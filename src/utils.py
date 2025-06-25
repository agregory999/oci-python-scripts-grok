import logging
import os

import oci


def setup_logging(verbose: bool) -> logging.Logger:
    """Set up logging based on verbose flag."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def initialize_oci() -> tuple[
    dict, oci.auth.signers.InstancePrincipalsSecurityTokenSigner | None
]:
    """Initialize OCI configuration, trying instance principal or config file."""
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
                raise FileNotFoundError(
                    f'OCI config file not found at {config_path}'
                ) from err
            try:
                config = oci.config.from_file(config_path, 'DEFAULT')
                oci.config.validate_config(config)
                signer = None
                logger.info('Initialized OCI with config file')
            except oci.exceptions.InvalidConfig as config_err:
                raise ValueError(
                    f'Invalid OCI config at {config_path}: {str(config_err)}'
                ) from config_err
    else:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f'OCI config file not found at {config_path}')
        try:
            config = oci.config.from_file(config_path, 'DEFAULT')
            oci.config.validate_config(config)
            signer = None
            logger.info('Initialized OCI with config file')
        except oci.exceptions.InvalidConfig as config_err:
            raise ValueError(
                f'Invalid OCI config at {config_path}: {str(config_err)}'
            ) from config_err

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
        raise RuntimeError(
            f'Failed to create OCI client {client_class.__name__}: {str(err)}'
        ) from err


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
