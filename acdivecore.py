"""
ACDIVE Core Engine - Main orchestration system
Architecture Rationale: Centralized orchestrator with fail-safe mechanisms
and comprehensive state management for autonomous cross-domain operations.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict
import json

from .firebase_client import FirebaseClient
from .domain_identifier import DomainIdentifier
from .component_discovery import ComponentDiscovery
from .integration_weaver import IntegrationWeaver
from .synaptic_modulator import DynamicSynapticModulator

logger = logging.getLogger(__name__)


@dataclass
class SystemState:
    """Immutable system state representation for consistency"""
    timestamp: datetime
    active_domains: List[str]
    component_count: int
    synapse_health: float
    last_error: Optional[str] = None
    operational_mode: str = "normal"


class ACDIVEEngine:
    """
    Main orchestrator for autonomous cross-domain integration.
    Implements circuit breaker pattern and graceful degradation.
    """
    
    def __init__(self, 
                 firebase_config: Optional[Dict[str, Any]] = None,
                 log_level: str = "INFO"):
        """
        Initialize the ACDIVE engine with dependency injection.
        
        Args:
            firebase_config: Firebase configuration dict. If None, loads from environment.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Raises:
            ValueError: If required dependencies are missing
            ConnectionError: If Firebase connection fails
        """
        self._setup_logging(log_level)
        logger.info("Initializing ACDIVE Engine v1.0.0")
        
        # Initialize state tracking
        self.state = SystemState(
            timestamp=datetime.now(),
            active_domains=[],
            component_count=0,
            synapse_health=1.0
        )
        
        # Circuit breaker state
        self.circuit_state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.max_failures = 5
        
        try:
            # Initialize Firebase client for state persistence
            self.firebase_client = FirebaseClient(config=firebase_config)
            
            # Initialize core components with dependency injection
            self.domain_identifier = DomainIdentifier(self.firebase_client)
            self.component_discovery = ComponentDiscovery(self.firebase_client)
            self.integration_weaver = IntegrationWeaver(self.firebase_client)
            self.synaptic_modulator = DynamicSynapticModulator(self.firebase_client)
            
            # Initialize component registry
            self.component_registry: Dict[str, Dict[str, Any]] = {}
            
            # Load initial state if available
            self._load_persisted_state()
            
            logger.info("ACDIVE Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ACDIVE Engine: {str(e)}")
            self._handle_initialization_failure(e)
            raise
    
    def _setup_logging(self, log_level: str) -> None:
        """Configure structured logging for observability"""
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.StreamHandler(),
                # In production, add FileHandler or Cloud Logging handler
            ]
        )
    
    def _handle_initialization_failure(self, error: Exception) -> None:
        """Graceful degradation on initialization failure"""
        logger.warning("Entering degraded mode - core functionality limited")
        self.state.operational_mode = "degraded"
        
        # Store minimal state in memory only
        self.firebase_client = None
        self.component_registry = {}
    
    def _load_persisted_state(self) -> None:
        """Load system state from persistent storage"""
        try:
            if self.firebase_client:
                state_data = self.firebase_client.get_document(
                    collection="system_state",
                    document_id="ac