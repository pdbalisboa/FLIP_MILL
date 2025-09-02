"""
Europeana API Client Package

A Python client for interacting with the Europeana Search API.
Provides a clean interface for searching cultural heritage items with support
for complex queries, faceting, and pagination.
"""

from .client import (
    EuropeanaClient,
    QueryBuilder,
    SearchResults,
    AggregateField,
    SearchField,
    MediaType,
    Profile,
    Reusability,
    RightsCategories,
    FACETABLE_FIELDS,
    DEFAULT_ROWS,
    MAX_ROWS,
    build_query_string,
)

from .models import (
    EuropeanaItem,
    WebResource,
    Aggregation,
    FacetField,
    Facet,
    StructuredSearchResults,
    EntityWebResource,
    EntityAggregation,
    PlaceEntity,
    LangMap,
)

__all__ = [
    # Client classes
    "EuropeanaClient",
    "QueryBuilder",
    "SearchResults",
    # Field enums
    "AggregateField",
    "SearchField",
    "MediaType",
    "Profile",
    "Reusability",
    "RightsCategories",
    # Constants
    "FACETABLE_FIELDS",
    "DEFAULT_ROWS",
    "MAX_ROWS",
    # Utility functions
    "build_query_string",
    # Data models
    "EuropeanaItem",
    "WebResource",
    "Aggregation",
    "FacetField",
    "Facet",
    "StructuredSearchResults",
    "EntityWebResource",
    "EntityAggregation",
    "PlaceEntity",
    "LangMap",
]
