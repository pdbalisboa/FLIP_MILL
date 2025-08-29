"""
Structured data models for Europeana API v2 responses.

This module defines dataclasses that represent the structure of items returned
from the Europeana Search API v2. The models are based on the Europeana Data Model (EDM)
and provide type-safe access to common metadata fields.

Based on Europeana API v2: https://api.europeana.eu/record/v2/search.json
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union

# Type alias for multilingual fields in Entity API
LangMap = Dict[str, Union[str, List[str]]]


@dataclass
class WebResource:
    """
    Represents a web resource associated with an item.

    Web resources are digital representations of cultural heritage objects,
    such as images, videos, or documents.
    """

    # Direct access URL to the resource
    web_resource_edm_rights: Optional[str] = None
    # Thumbnail or preview URL
    web_resource_dc_rights: Optional[str] = None
    # Format/MIME type of the resource
    web_resource_dc_format: Optional[str] = None
    # Additional web resource properties
    about: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebResource":
        """Create WebResource from API response dictionary."""
        return cls(
            web_resource_edm_rights=data.get("webResourceEdmRights"),
            web_resource_dc_rights=data.get("webResourceDcRights"),
            web_resource_dc_format=data.get("webResourceDcFormat"),
            about=data.get("about"),
        )


@dataclass
class Aggregation:
    """
    Represents aggregation information for an item.

    Aggregations group together the Cultural Heritage Object (CHO)
    with its digital representations and metadata.
    """

    # URL that shows the object in the provider's interface
    edm_is_shown_by: Optional[str] = None
    # URL of the provider page about the object
    edm_is_shown_at: Optional[str] = None
    # Direct link to the object
    edm_object: Optional[str] = None
    # Aggregated web resources
    web_resources: List[WebResource] = field(default_factory=list)
    # Rights statement for the aggregation
    edm_rights: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Aggregation":
        """Create Aggregation from API response dictionary."""
        web_resources = []
        if "webResources" in data:
            web_resources = [WebResource.from_dict(wr) for wr in data["webResources"]]

        return cls(
            edm_is_shown_by=data.get("edmIsShownBy"),
            edm_is_shown_at=data.get("edmIsShownAt"),
            edm_object=data.get("edmObject"),
            web_resources=web_resources,
            edm_rights=data.get("edmRights"),
        )


@dataclass
class EuropeanaItem:
    """
    Represents a single item from Europeana search results.

    This dataclass structures the JSON response from the Europeana API into
    typed fields based on the Europeana Data Model (EDM). Fields may be
    strings or lists of strings depending on the source metadata.
    """

    # Core identification
    id: Optional[str] = None
    type: Optional[Union[str, List[str]]] = None
    guid: Optional[str] = None
    link: Optional[str] = None

    # Title information - from dc:title
    title: Optional[Union[str, List[str]]] = None

    # Creator information - from dc:creator
    dc_creator: Optional[Union[str, List[str]]] = None
    dc_contributor: Optional[Union[str, List[str]]] = None

    # Subject/topic information - from dc:subject
    dc_subject: Optional[Union[str, List[str]]] = None

    # Description - from dc:description
    dc_description: Optional[Union[str, List[str]]] = None

    # Date/year information
    year: Optional[Union[str, List[str]]] = None

    # Geographic information
    country: Optional[Union[str, List[str]]] = None
    place: Optional[Union[str, List[str]]] = None
    dcterms_spatial: Optional[Union[str, List[str]]] = None

    # Provider information
    data_provider: Optional[Union[str, List[str]]] = None
    edm_data_provider: Optional[Union[str, List[str]]] = None
    provider: Optional[Union[str, List[str]]] = None

    # Media and access URLs
    edm_preview: Optional[Union[str, List[str]]] = None
    edm_is_shown_by: Optional[Union[str, List[str]]] = None
    edm_is_shown_at: Optional[Union[str, List[str]]] = None

    # Rights information
    rights: Optional[Union[str, List[str]]] = None
    edm_rights: Optional[Union[str, List[str]]] = None

    # Language information
    dc_language: Optional[Union[str, List[str]]] = None
    language: Optional[Union[str, List[str]]] = None

    # Format information
    dc_format: Optional[Union[str, List[str]]] = None

    # Current location with coordinates
    edm_current_location: Optional[Union[str, List[str]]] = None

    # Language-aware fields (multilingual metadata)
    dc_creator_lang_aware: Optional[Dict[str, Any]] = None
    dc_contributor_lang_aware: Optional[Dict[str, Any]] = None
    dc_description_lang_aware: Optional[Dict[str, Any]] = None
    dc_language_lang_aware: Optional[Dict[str, Any]] = None
    dc_subject_lang_aware: Optional[Dict[str, Any]] = None
    dc_title_lang_aware: Optional[Dict[str, Any]] = None
    dc_type_lang_aware: Optional[Dict[str, Any]] = None

    # EDM Concepts (controlled vocabularies)
    edm_concept: Optional[Union[str, List[str]]] = None
    edm_concept_label: Optional[Union[str, List[str]]] = None
    edm_concept_pref_label_lang_aware: Optional[Dict[str, Any]] = None

    # EDM Agents (people, organizations)
    edm_agent: Optional[Union[str, List[str]]] = None
    edm_agent_label: Optional[Union[str, List[str]]] = None
    edm_agent_label_lang_aware: Optional[Dict[str, Any]] = None

    # EDM Places (geographic entities)
    edm_place: Optional[Union[str, List[str]]] = None
    edm_place_label: Optional[Union[str, List[str]]] = None
    edm_place_alt_label: Optional[Union[str, List[str]]] = None
    edm_place_label_lang_aware: Optional[Dict[str, Any]] = None
    edm_place_alt_label_lang_aware: Optional[Dict[str, Any]] = None
    edm_place_latitude: Optional[Union[str, List[str]]] = None
    edm_place_longitude: Optional[Union[str, List[str]]] = None

    # EDM Timespans (time periods)
    edm_timespan: Optional[Union[str, List[str]]] = None
    edm_timespan_label: Optional[Union[str, List[str]]] = None
    edm_timespan_label_lang_aware: Optional[Dict[str, Any]] = None

    # Collection and dataset information
    edm_dataset_name: Optional[Union[str, List[str]]] = None
    europeana_collection_name: Optional[Union[str, List[str]]] = None

    # Organizations involved
    organizations: Optional[Union[str, List[str]]] = None

    # Quality and completeness metrics
    completeness: Optional[int] = None
    europeana_completeness: Optional[int] = None
    score: Optional[float] = None

    # Search and indexing metadata
    index: Optional[int] = None

    # Timestamps and versioning
    timestamp: Optional[int] = None
    timestamp_created: Optional[str] = None
    timestamp_created_epoch: Optional[int] = None
    timestamp_update: Optional[str] = None
    timestamp_update_epoch: Optional[int] = None

    # User-generated content flag
    ugc: Optional[Union[bool, List[bool]]] = None

    # Preview distribution flag
    preview_no_distribute: Optional[bool] = None

    # Aggregation information
    aggregations: List[Aggregation] = field(default_factory=list)

    # Web resources
    web_resources: List[WebResource] = field(default_factory=list)

    # Raw data for fields not explicitly modeled
    _raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EuropeanaItem":
        """
        Create EuropeanaItem from API response dictionary.

        Args:
            data: Raw JSON dictionary from Europeana API

        Returns:
            EuropeanaItem instance with parsed fields
        """
        # Parse aggregations
        aggregations = []
        if "aggregations" in data:
            aggregations = [Aggregation.from_dict(agg) for agg in data["aggregations"]]

        # Parse web resources
        web_resources = []
        if "webResources" in data:
            web_resources = [WebResource.from_dict(wr) for wr in data["webResources"]]

        return cls(
            # Core identification
            id=data.get("id"),
            type=data.get("type"),
            guid=data.get("guid"),
            link=data.get("link"),
            # Basic metadata
            title=data.get("title"),
            dc_creator=data.get("dcCreator"),
            dc_contributor=data.get("dcContributor"),
            dc_subject=data.get("dcSubject"),
            dc_description=data.get("dcDescription"),
            year=data.get("year"),
            # Geographic
            country=data.get("country"),
            place=data.get("place"),
            dcterms_spatial=data.get("dctermsSpatial"),
            # Providers
            data_provider=data.get("dataProvider"),
            edm_data_provider=data.get("edmDataProvider"),
            provider=data.get("provider"),
            # Media URLs
            edm_preview=data.get("edmPreview"),
            edm_is_shown_by=data.get("edmIsShownBy"),
            edm_is_shown_at=data.get("edmIsShownAt"),
            # Rights
            rights=data.get("rights"),
            edm_rights=data.get("edmRights"),
            # Language
            dc_language=data.get("dcLanguage"),
            language=data.get("language"),
            dc_format=data.get("dcFormat"),
            edm_current_location=data.get("edmCurrentLocation"),
            # Language-aware fields
            dc_creator_lang_aware=data.get("dcCreatorLangAware"),
            dc_contributor_lang_aware=data.get("dcContributorLangAware"),
            dc_description_lang_aware=data.get("dcDescriptionLangAware"),
            dc_language_lang_aware=data.get("dcLanguageLangAware"),
            dc_subject_lang_aware=data.get("dcSubjectLangAware"),
            dc_title_lang_aware=data.get("dcTitleLangAware"),
            dc_type_lang_aware=data.get("dcTypeLangAware"),
            # EDM entities
            edm_concept=data.get("edmConcept"),
            edm_concept_label=data.get("edmConceptLabel"),
            edm_concept_pref_label_lang_aware=data.get("edmConceptPrefLabelLangAware"),
            edm_agent=data.get("edmAgent"),
            edm_agent_label=data.get("edmAgentLabel"),
            edm_agent_label_lang_aware=data.get("edmAgentLabelLangAware"),
            edm_place=data.get("edmPlace"),
            edm_place_label=data.get("edmPlaceLabel"),
            edm_place_alt_label=data.get("edmPlaceAltLabel"),
            edm_place_label_lang_aware=data.get("edmPlaceLabelLangAware"),
            edm_place_alt_label_lang_aware=data.get("edmPlaceAltLabelLangAware"),
            edm_place_latitude=data.get("edmPlaceLatitude"),
            edm_place_longitude=data.get("edmPlaceLongitude"),
            edm_timespan=data.get("edmTimespan"),
            edm_timespan_label=data.get("edmTimespanLabel"),
            edm_timespan_label_lang_aware=data.get("edmTimespanLabelLangAware"),
            # Collections
            edm_dataset_name=data.get("edmDatasetName"),
            europeana_collection_name=data.get("europeanaCollectionName"),
            organizations=data.get("organizations"),
            # Quality metrics
            completeness=data.get("completeness"),
            europeana_completeness=data.get("europeanaCompleteness"),
            score=data.get("score"),
            index=data.get("index"),
            # Timestamps
            timestamp=data.get("timestamp"),
            timestamp_created=data.get("timestamp_created"),
            timestamp_created_epoch=data.get("timestamp_created_epoch"),
            timestamp_update=data.get("timestamp_update"),
            timestamp_update_epoch=data.get("timestamp_update_epoch"),
            # Flags
            ugc=data.get("ugc"),
            preview_no_distribute=data.get("previewNoDistribute"),
            # Complex structures
            aggregations=aggregations,
            web_resources=web_resources,
            _raw_data=data,
        )

    def get_first_title(self) -> str:
        """Get the first title, handling both string and list formats."""
        if not self.title:
            return "Untitled"
        if isinstance(self.title, list):
            return self.title[0] if self.title else "Untitled"
        return self.title

    def get_first_creator(self) -> str:
        """Get the first creator, handling both string and list formats."""
        if not self.dc_creator:
            return "Unknown creator"
        if isinstance(self.dc_creator, list):
            return self.dc_creator[0] if self.dc_creator else "Unknown creator"
        return self.dc_creator

    def get_first_country(self) -> str:
        """Get the first country, handling both string and list formats."""
        if not self.country:
            return "Unknown"
        if isinstance(self.country, list):
            return self.country[0] if self.country else "Unknown"
        return self.country

    def get_first_year(self) -> str:
        """Get the first year, handling both string and list formats."""
        if not self.year:
            return "Unknown year"
        if isinstance(self.year, list):
            return self.year[0] if self.year else "Unknown year"
        return str(self.year)

    def get_coordinates(self) -> Optional[tuple[float, float]]:
        """Extract coordinates from EDM place fields if available."""
        if self.edm_place_latitude and self.edm_place_longitude:
            try:
                lat = (
                    self.edm_place_latitude[0]
                    if isinstance(self.edm_place_latitude, list)
                    else self.edm_place_latitude
                )
                lon = (
                    self.edm_place_longitude[0]
                    if isinstance(self.edm_place_longitude, list)
                    else self.edm_place_longitude
                )
                return (float(lat), float(lon))
            except (ValueError, TypeError, IndexError):
                return None
        return None

    def get_creation_timestamp(self) -> Optional[int]:
        """Get the creation timestamp in epoch format."""
        return self.timestamp_created_epoch

    def get_update_timestamp(self) -> Optional[int]:
        """Get the last update timestamp in epoch format."""
        return self.timestamp_update_epoch

    def get_rights_uris(self) -> List[str]:
        """Extract all rights URIs from the item."""
        uris = []

        # Check main rights field
        if self.rights:
            rights_list = (
                self.rights if isinstance(self.rights, list) else [self.rights]
            )
            for right in rights_list:
                if isinstance(right, str) and right.startswith(("http", "https")):
                    uris.append(right)

        # Check EDM rights field
        if self.edm_rights:
            edm_rights_list = (
                self.edm_rights
                if isinstance(self.edm_rights, list)
                else [self.edm_rights]
            )
            for right in edm_rights_list:
                if isinstance(right, str) and right.startswith(("http", "https")):
                    uris.append(right)

        # Check web resources
        for wr in self.web_resources:
            if wr.web_resource_edm_rights and wr.web_resource_edm_rights.startswith(
                ("http", "https")
            ):
                uris.append(wr.web_resource_edm_rights)

        return list(set(uris))  # Remove duplicates  # Remove duplicates


@dataclass
class FacetField:
    """Represents a single field within a facet."""

    label: str
    count: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FacetField":
        """Create FacetField from API response dictionary."""
        return cls(label=data.get("label", ""), count=data.get("count", 0))


@dataclass
class Facet:
    """Represents a facet in search results."""

    name: str
    fields: List[FacetField] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Facet":
        """Create Facet from API response dictionary."""
        fields = []
        if "fields" in data:
            fields = [FacetField.from_dict(f) for f in data["fields"]]

        return cls(name=data.get("name", ""), fields=fields)


@dataclass
class StructuredSearchResults:
    """
    Container for Europeana search results with structured items.

    This replaces the basic SearchResults class with typed EuropeanaItem instances
    instead of raw dictionaries.
    """

    items: List[EuropeanaItem]
    total_results: int
    next_cursor: Optional[str] = None
    facets: Optional[List[Facet]] = None
    query: Optional[str] = None

    def __len__(self) -> int:
        """Return the number of items in this result set."""
        return len(self.items)

    def __iter__(self):
        """Iterate over items in the result set."""
        return iter(self.items)

    @classmethod
    def from_search_results(
        cls, search_results, parse_items: bool = True
    ) -> "StructuredSearchResults":
        """
        Convert a basic SearchResults instance to StructuredSearchResults.

        Args:
            search_results: SearchResults instance with raw dictionaries
            parse_items: Whether to parse items into EuropeanaItem instances

        Returns:
            StructuredSearchResults with parsed items
        """
        items = []
        if parse_items:
            items = [EuropeanaItem.from_dict(item) for item in search_results.items]

        facets = None
        if search_results.facets:
            facets = [Facet.from_dict(f) for f in search_results.facets]

        return cls(
            items=items,
            total_results=search_results.total_results,
            next_cursor=search_results.next_cursor,
            facets=facets,
            query=search_results.query,
        )


@dataclass
class EntityWebResource:
    """
    Represents a web resource in Entity API responses.

    Used for depiction and isShownBy fields in place entities.
    """

    id: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None
    thumbnail: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityWebResource":
        """Create EntityWebResource from API response dictionary."""
        return cls(
            id=data.get("id"),
            type=data.get("type"),
            source=data.get("source"),
            thumbnail=data.get("thumbnail"),
        )


@dataclass
class EntityAggregation:
    """
    Represents aggregation information for an entity.

    Contains metadata about the entity's aggregation including creation dates,
    page rank, record counts, and aggregated sources.
    """

    id: Optional[str] = None
    type: Optional[str] = None
    created: Optional[str] = None
    modified: Optional[str] = None
    page_rank: Optional[float] = None
    record_count: Optional[int] = None
    score: Optional[int] = None
    aggregates: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntityAggregation":
        """Create EntityAggregation from API response dictionary."""
        return cls(
            id=data.get("id"),
            type=data.get("type"),
            created=data.get("created"),
            modified=data.get("modified"),
            page_rank=data.get("pageRank"),
            record_count=data.get("recordCount"),
            score=data.get("score"),
            aggregates=data.get("aggregates", []),
        )


@dataclass
class PlaceEntity:
    """
    Represents a place entity from the Europeana Entity API.

    A place entity describes a physical location associated with cultural heritage objects.
    Contains geographic coordinates, multilingual labels, and relationships to other entities.
    """

    # Core fields
    id: Optional[str] = None
    type: Optional[str] = None
    context: Optional[str] = None  # @context field from JSON-LD

    # Visual resources
    depiction: Optional[EntityWebResource] = None
    is_shown_by: Optional[EntityWebResource] = None

    # Multilingual labels
    pref_label: Optional[LangMap] = None
    alt_label: Optional[LangMap] = None

    # Geographic coordinates
    lat: Optional[float] = None
    long: Optional[float] = None
    alt: Optional[float] = None

    # Descriptive information
    note: Optional[LangMap] = None

    # Relationships to other entities
    has_part: List[str] = field(default_factory=list)
    is_part_of: List[str] = field(default_factory=list)
    is_next_in_sequence: List[str] = field(default_factory=list)

    # External linking
    same_as: List[str] = field(default_factory=list)
    in_scheme: List[str] = field(default_factory=list)

    # Aggregation information
    is_aggregated_by: Optional[EntityAggregation] = None

    def get_name(self, language: str):
        if self.pref_label and language in self.pref_label.keys():
            return self.pref_label[language]
        else:
            raise ValueError(f"No prefLabel for language '{language}'")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlaceEntity":
        """Create PlaceEntity from Entity API response dictionary."""
        # Handle web resources
        depiction = None
        if "depiction" in data and data["depiction"]:
            depiction = EntityWebResource.from_dict(data["depiction"])

        is_shown_by = None
        if "isShownBy" in data and data["isShownBy"]:
            is_shown_by = EntityWebResource.from_dict(data["isShownBy"])

        # Handle aggregation
        is_aggregated_by = None
        if "isAggregatedBy" in data and data["isAggregatedBy"]:
            is_aggregated_by = EntityAggregation.from_dict(data["isAggregatedBy"])

        return cls(
            id=data.get("id"),
            type=data.get("type"),
            context=data.get("@context"),
            depiction=depiction,
            is_shown_by=is_shown_by,
            pref_label=data.get("prefLabel"),
            alt_label=data.get("altLabel"),
            lat=data.get("lat"),
            long=data.get("long"),
            alt=data.get("alt"),
            note=data.get("note"),
            has_part=data.get("hasPart", []),
            is_part_of=data.get("isPartOf", []),
            is_next_in_sequence=data.get("isNextInSequence", []),
            same_as=data.get("sameAs", []),
            in_scheme=data.get("inScheme", []),
            is_aggregated_by=is_aggregated_by,
        )
