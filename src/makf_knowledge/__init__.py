"""World-model-agnostic multiperspective action knowledge (P1.1–E1)."""
__version__ = '0.1.0'
from .validation import SemanticValidator, ValidationError, validate_file
from .guidance import build_context
from .ontology import list_ontologies, describe_class, ontology_graph
__all__ = ['SemanticValidator','ValidationError','validate_file','build_context','list_ontologies','describe_class','ontology_graph']
