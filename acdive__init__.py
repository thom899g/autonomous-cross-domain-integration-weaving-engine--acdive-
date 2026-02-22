"""
Autonomous Cross-Domain Integration Weaving Engine (ACDIVE)
Version: 1.0.0
"""

from .core import ACDIVEEngine
from .domain_identifier import DomainIdentifier
from .component_discovery import ComponentDiscovery
from .integration_weaver import IntegrationWeaver
from .synaptic_modulator import DynamicSynapticModulator

__version__ = "1.0.0"
__all__ = [
    'ACDIVEEngine',
    'DomainIdentifier',
    'ComponentDiscovery',
    'IntegrationWeaver',
    'DynamicSynapticModulator'
]