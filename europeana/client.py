"""
Europeana Search API Client Library

A Python client for interacting with the Europeana Search API.
Provides a clean interface for searching cultural heritage items with support
for complex queries, faceting, and pagination.
"""

import copy
import re
from typing import Dict, List, Optional, Iterator, Union, Tuple
from dataclasses import dataclass
from enum import Enum, StrEnum
import httpx

from .models import EuropeanaItem, StructuredSearchResults, PlaceEntity


# Field Enums
class AggregateField(StrEnum):
    """Aggregated search fields that search across multiple metadata fields."""

    TITLE = "title"  # Searches all title fields
    SUBJECT = "subject"  # Searches all subject fields
    WHO = "who"  # Creator/contributor names
    WHAT = "what"  # Subject/topic/type
    WHEN = "when"  # Dates/time periods
    WHERE = "where"  # Geographic locations
    TEXT = "text"  # Free text search


class SearchField(StrEnum):
    """All available search fields from Europeana API."""

    # Basic Europeana fields
    EUROPEANA_ID = "europeana_id"
    TIMESTAMP = "timestamp"
    TIMESTAMP_CREATED = "timestamp_created"
    TIMESTAMP_UPDATE = "timestamp_update"
    EUROPEANA_COMPLETENESS = "europeana_completeness"
    COMPLETENESS = "COMPLETENESS"

    # Dublin Core proxy fields
    PROXY_DC_CREATOR_WILDCARD = "proxy_dc_creator.*"
    PROXY_DC_CONTRIBUTOR = "proxy_dc_contributor"
    CONTRIBUTOR = "CONTRIBUTOR"
    PROXY_DC_COVERAGE = "proxy_dc_coverage"
    PROXY_DC_CREATOR = "proxy_dc_creator"
    PROXY_DC_DATE = "proxy_dc_date"
    PROXY_DC_DESCRIPTION = "proxy_dc_description"
    PROXY_DC_FORMAT = "proxy_dc_format"
    PROXY_DC_IDENTIFIER = "proxy_dc_identifier"
    LANGUAGE = "LANGUAGE"
    PROXY_DC_PUBLISHER = "proxy_dc_publisher"
    PROXY_DC_RIGHTS = "proxy_dc_rights"
    PROXY_DC_SOURCE = "proxy_dc_source"
    PROXY_DC_SUBJECT = "proxy_dc_subject"
    PROXY_DC_TITLE = "proxy_dc_title"
    PROXY_DC_TYPE = "proxy_dc_type"
    PROXY_DC_TYPE_SEARCH = "proxy_dc_type_search"

    # Dublin Core Terms proxy fields
    PROXY_DCTERMS_ALTERNATIVE = "proxy_dcterms_alternative"
    PROXY_DCTERMS_CREATED = "proxy_dcterms_created"
    PROXY_DCTERMS_HASPART = "proxy_dcterms_hasPart"
    PROXY_DCTERMS_ISPARTOF = "proxy_dcterms_isPartOf"
    PROXY_DCTERMS_ISSUED = "proxy_dcterms_issued"
    PROXY_DCTERMS_MEDIUM = "proxy_dcterms_medium"
    PROXY_DCTERMS_PROVENANCE = "proxy_dcterms_provenance"
    PROXY_DCTERMS_SPATIAL = "proxy_dcterms_spatial"
    PROXY_DCTERMS_TEMPORAL = "proxy_dcterms_temporal"

    # EDM proxy fields
    PROXY_EDM_CURRENTLOCATION = "proxy_edm_currentLocation"
    PROXY_EDM_HASMET = "proxy_edm_hasMet"
    PROXY_EDM_ISRELATEDTO = "proxy_edm_isRelatedTo"

    # Filter fields
    TYPE = "TYPE"
    YEAR = "YEAR"
    DATA_PROVIDER = "DATA_PROVIDER"
    PROVIDER_AGGREGATION_EDM_HASVIEW = "provider_aggregation_edm_hasView"
    PROVIDER_AGGREGATION_EDM_INTERMEDIATEPROVIDER = (
        "provider_aggregation_edm_intermediateProvider"
    )
    PROVIDER_AGGREGATION_EDM_ISSHOWNAT = "provider_aggregation_edm_isShownAt"
    PROVIDER_AGGREGATION_EDM_ISSHOWNBY = "provider_aggregation_edm_isShownBy"
    PROVIDER_AGGREGATION_EDM_OBJECT = "provider_aggregation_edm_object"
    PROVIDER = "PROVIDER"
    PROVIDER_AGGREGATION_DC_RIGHTS = "provider_aggregation_dc_rights"
    RIGHTS = "RIGHTS"
    UGC = "UGC"
    EDM_PREVIEWNODISTRIBUTE = "edm_previewNoDistribute"
    EUROPEANA_COLLECTIONNAME = "europeana_collectionName1"
    EDM_DATASETNAME = "edm_datasetName"
    COUNTRY = "COUNTRY"
    EUROPEANA_AGGREGATION_EDM_LANGUAGE = "europeana_aggregation_edm_language"

    # Web resource fields
    EDM_WEBRESOURCE = "edm_webResource"
    WR_DC_RIGHTS = "wr_dc_rights"
    WR_DCTERMS_ISREFERENCEDBY = "wr_dcterms_isReferencedBy"
    WR_EDM_ISNEXTINSEQUENCE = "wr_edm_isNextInSequence"
    WR_EDM_RIGHTS = "wr_edm_rights"
    WR_SVCS_HASSERVICE = "wr_svcs_hasservice"
    WR_CC_LICENSE = "wr_cc_license"
    PROVIDER_AGGREGATION_CC_LICENSE = "provider_aggregation_cc_license"
    PROVIDER_AGGREGATION_ODRL_INHERITED_FROM = (
        "provider_aggregation_odrl_inherited_from"
    )
    WR_CC_ODRL_INHERITED_FROM = "wr_cc_odrl_inherited_from"
    WR_CC_DEPRECATED_ON = "wr_cc_deprecated_on"
    PROVIDER_AGGREGATION_CC_DEPRECATED_ON = "provider_aggregation_cc_deprecated_on"

    # Service fields
    SVCS_SERVICE = "svcs_service"
    SV_DCTERMS_CONFORMSTO = "sv_dcterms_conformsTo"

    # Agent fields
    EDM_AGENT = "edm_agent"
    AG_SKOS_PREFLABEL = "ag_skos_prefLabel"
    AG_SKOS_ALTLABEL = "ag_skos_altLabel"
    AG_FOAF_NAME = "ag_foaf_name"
    AG_RDAGR2_DATEOFBIRTH = "ag_rdagr2_dateOfBirth"
    AG_RDAGR2_DATEOFDEATH = "ag_rdagr2_dateOfDeath"
    AG_RDAGR2_PLACEOFBIRTH = "ag_rdagr2_placeOfBirth"
    AG_RDAGR2_PLACEOFDEATH = "ag_rdagr2_placeOfDeath"
    AG_RDAGR2_PROFESSIONOROCCUPATION = "ag_rdagr2_professionOrOccupation"

    # Concept fields
    SKOS_CONCEPT = "skos_concept"
    CC_SKOS_PREFLABEL = "cc_skos_prefLabel"
    CC_SKOS_ALTLABEL = "cc_skos_altLabel"

    # Place fields
    EDM_PLACE = "edm_place"
    PL_WGS84_POS_LAT = "pl_wgs84_pos_lat"
    PL_WGS84_POS_LONG = "pl_wgs84_pos_long"
    PL_WGS84_POS_ALT = "pl_wgs84_pos_alt"
    PL_SKOS_PREFLABEL = "pl_skos_prefLabel"
    PL_SKOS_ALTLABEL = "pl_skos_altLabel"

    # Timespan fields
    EDM_TIMESPAN = "edm_timespan"
    TS_SKOS_PREFLABEL = "ts_skos_prefLabel"
    TS_SKOS_ALTLABEL = "ts_skos_altLabel"


# Enums
class MediaType(Enum):
    """Available media types for filtering."""

    IMAGE = "IMAGE"
    SOUND = "SOUND"
    VIDEO = "VIDEO"
    TEXT = "TEXT"
    THREE_D = "3D"


class Profile(Enum):
    """Response detail levels."""

    MINIMAL = "minimal"  # Basic metadata only
    STANDARD = "standard"  # Standard metadata
    RICH = "rich"  # Full metadata including all available fields
    FACETS = "facets"  # Include facet counts in response


class Reusability(Enum):
    """Content reusability categories."""

    OPEN = "open"  # Freely reusable content
    RESTRICTED = "restricted"  # Content with some restrictions
    PERMISSION = "permission"  # Requires explicit permission


class RightsCategories:
    """Common rights patterns and URIs for filtering."""

    # Patterns for wildcard searches
    PUBLIC_DOMAIN = "*public*"
    CREATIVE_COMMONS = "*creative*"
    COPYRIGHT = "*copyright*"

    # Public Domain URIs
    PDM_URI = "http://creativecommons.org/publicdomain/mark/1.0/"
    CC0_URI = "http://creativecommons.org/publicdomain/zero/1.0/"

    # Creative Commons License URIs (version agnostic patterns)
    CC_BY = "http://creativecommons.org/licenses/by/*"
    CC_BY_SA = "http://creativecommons.org/licenses/by-sa/*"
    CC_BY_ND = "http://creativecommons.org/licenses/by-nd/*"
    CC_BY_NC = "http://creativecommons.org/licenses/by-nc/*"
    CC_BY_NC_SA = "http://creativecommons.org/licenses/by-nc-sa/*"
    CC_BY_NC_ND = "http://creativecommons.org/licenses/by-nc-nd/*"

    # Rights Statements URIs
    IN_COPYRIGHT = "http://rightsstatements.org/vocab/InC/1.0/"
    IN_COPYRIGHT_EU_ORPHAN = "http://rightsstatements.org/vocab/InC-OW-EU/1.0/"
    IN_COPYRIGHT_EDUCATIONAL = "http://rightsstatements.org/vocab/InC-EDU/1.0/"
    IN_COPYRIGHT_NON_COMMERCIAL = "http://rightsstatements.org/vocab/InC-NC/1.0/"
    NO_COPYRIGHT_CONTRACTUAL = "http://rightsstatements.org/vocab/NoC-CR/1.0/"
    NO_COPYRIGHT_OTHER = "http://rightsstatements.org/vocab/NoC-OKLR/1.0/"
    NO_KNOWN_COPYRIGHT = "http://rightsstatements.org/vocab/NKC/1.0/"
    COPYRIGHT_NOT_EVALUATED = "http://rightsstatements.org/vocab/CNE/1.0/"
    COPYRIGHT_UNDETERMINED = "http://rightsstatements.org/vocab/UND/1.0/"


# Facetable fields list
FACETABLE_FIELDS = [
    SearchField.PROXY_DC_CREATOR,
    SearchField.PROXY_DC_CONTRIBUTOR,
    SearchField.PROXY_DC_SUBJECT,
    SearchField.PROXY_DC_TYPE,
    SearchField.PROXY_DC_RIGHTS,
    SearchField.PROXY_DCTERMS_MEDIUM,
    SearchField.PROXY_DCTERMS_SPATIAL,
    SearchField.TYPE,
    SearchField.PROVIDER,
    SearchField.DATA_PROVIDER,
    SearchField.RIGHTS,
    SearchField.COUNTRY,
    SearchField.LANGUAGE,
]


# Module-level constants
DEFAULT_ROWS = 100
MAX_ROWS = 100


def build_query_string(
    text: Optional[str] = None,
    filters: Optional[Dict[str, Union[str, Enum]]] = None,
) -> str:
    """
    Build a Lucene query string from text and filters.

    Args:
        text: Free text search query
        filters: Dictionary of field:value filters (values can be strings or enums)

    Returns:
        Combined query string
    """
    query_parts = []

    # Add free text if provided
    if text:
        query_parts.append(text)

    # Add filters
    if filters:
        for field, value in filters.items():
            # Handle enum values
            if hasattr(value, "value"):  # Check if it's an enum
                value = value.value

            # Convert to string if not already
            value = str(value)

            # Handle special fields that might need quotes
            if " " in value and not (value.startswith('"') and value.endswith('"')):
                value = f'"{value}"'
            query_parts.append(f"{field}:{value}")

    # Combine with AND
    return " AND ".join(query_parts) if query_parts else ""


@dataclass
class SearchResults:
    """Container for Europeana search results with pagination info."""

    items: List[Dict]
    total_results: int
    next_cursor: Optional[str] = None
    facets: Optional[Dict] = None
    query: Optional[str] = None

    def __len__(self) -> int:
        """Return the number of items in this result set."""
        return len(self.items)

    def __iter__(self) -> Iterator[Dict]:
        """Iterate over items in the result set."""
        return iter(self.items)


class QueryBuilder:
    """Fluent interface for building Europeana search queries."""

    def __init__(self):
        """Initialize QueryBuilder."""
        self._filters = {}
        self._text_query = None
        self._geographic = None
        self._facets = []
        self._profile = Profile.RICH
        self._rows = DEFAULT_ROWS
        self._reusability = None
        self._media_flag = None
        self._thumbnail_flag = None

    def who(self, name: str) -> "QueryBuilder":
        """Add creator/artist filter."""
        self._filters[AggregateField.WHO] = name
        return self

    def where(self, place: str) -> "QueryBuilder":
        """Add geographic location filter."""
        self._filters[AggregateField.WHERE] = place
        return self

    def what(self, topic: str) -> "QueryBuilder":
        """Add subject/topic filter."""
        self._filters[AggregateField.WHAT] = topic
        return self

    def title(self, title: str) -> "QueryBuilder":
        """Add title filter."""
        self._filters[AggregateField.TITLE] = title
        return self

    def when(self, time_description: str) -> "QueryBuilder":
        """Add temporal description filter."""
        self._filters[AggregateField.WHEN] = time_description
        return self

    def text(self, text: str) -> "QueryBuilder":
        """Set free text search query."""
        self._filters[AggregateField.TEXT] = text
        return self

    def media_type(self, media_type: Union[str, MediaType]) -> "QueryBuilder":
        """Add media type filter."""
        if isinstance(media_type, MediaType):
            media_type = media_type.value
        self._filters[SearchField.TYPE] = media_type
        return self

    def time_period(
        self, start_year: Optional[int] = None, end_year: Optional[int] = None
    ) -> "QueryBuilder":
        """Add time period filter with year range."""
        if start_year and end_year:
            self._filters[SearchField.YEAR] = f"[{start_year} TO {end_year}]"
        elif start_year:
            self._filters[SearchField.YEAR] = f"[{start_year} TO *]"
        elif end_year:
            self._filters[SearchField.YEAR] = f"[* TO {end_year}]"
        return self

    def public_domain(self) -> "QueryBuilder":
        """Filter for public domain items only."""
        self._filters[SearchField.RIGHTS] = (
            f"({RightsCategories.PDM_URI} OR {RightsCategories.CC0_URI})"
        )
        self._reusability = Reusability.OPEN
        return self

    def creative_commons(self, license_type: Optional[str] = None) -> "QueryBuilder":
        """Filter for Creative Commons licensed items."""
        if license_type:
            license_map = {
                "by": RightsCategories.CC_BY,
                "by-sa": RightsCategories.CC_BY_SA,
                "by-nd": RightsCategories.CC_BY_ND,
                "by-nc": RightsCategories.CC_BY_NC,
                "by-nc-sa": RightsCategories.CC_BY_NC_SA,
                "by-nc-nd": RightsCategories.CC_BY_NC_ND,
            }
            rights_filter = license_map.get(
                license_type.lower(), RightsCategories.CREATIVE_COMMONS
            )
        else:
            rights_filter = RightsCategories.CREATIVE_COMMONS
        self._filters[SearchField.RIGHTS] = rights_filter
        return self

    def institution(self, name: str, as_provider: bool = False) -> "QueryBuilder":
        """Filter by contributing institution."""
        field = SearchField.PROVIDER if as_provider else SearchField.DATA_PROVIDER
        self._filters[field] = name
        return self

    def quality(self, min_score: int = 8) -> "QueryBuilder":
        """Filter by metadata quality score (0-10)."""
        self._filters[SearchField.EUROPEANA_COMPLETENESS] = f"[{min_score} TO 10]"
        return self

    def field(self, field_name: str, value: str) -> "QueryBuilder":
        """Add generic field filter."""
        self._filters[field_name] = value
        return self

    # Individual SearchField methods
    def europeana_id(self, value: str) -> "QueryBuilder":
        """Filter by Europeana ID of the record."""
        self._filters[SearchField.EUROPEANA_ID] = value
        return self

    def timestamp(self, value: str) -> "QueryBuilder":
        """Filter by timestamp."""
        self._filters[SearchField.TIMESTAMP] = value
        return self

    def timestamp_created(self, value: str) -> "QueryBuilder":
        """Filter by the date when record was created (formatted as ISO 8601)."""
        self._filters[SearchField.TIMESTAMP_CREATED] = value
        return self

    def timestamp_update(self, value: str) -> "QueryBuilder":
        """Filter by the date when record was last updated (formatted as ISO 8601)."""
        self._filters[SearchField.TIMESTAMP_UPDATE] = value
        return self

    def completeness_score(self, value: Union[int, str]) -> "QueryBuilder":
        """Filter by Europeana measure of metadata completeness (1-10)."""
        self._filters[SearchField.EUROPEANA_COMPLETENESS] = str(value)
        return self

    def completeness(self, value: str) -> "QueryBuilder":
        """Filter by completeness field."""
        self._filters[SearchField.COMPLETENESS] = value
        return self

    def dc_creator_wildcard(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core creator with wildcard support."""
        self._filters[SearchField.PROXY_DC_CREATOR_WILDCARD] = value
        return self

    def dc_contributor(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core contributor."""
        self._filters[SearchField.PROXY_DC_CONTRIBUTOR] = value
        return self

    def contributor(self, value: str) -> "QueryBuilder":
        """Filter by contributor field."""
        self._filters[SearchField.CONTRIBUTOR] = value
        return self

    def dc_coverage(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core coverage."""
        self._filters[SearchField.PROXY_DC_COVERAGE] = value
        return self

    def dc_creator(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core creator."""
        self._filters[SearchField.PROXY_DC_CREATOR] = value
        return self

    def dc_date(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core date."""
        self._filters[SearchField.PROXY_DC_DATE] = value
        return self

    def dc_description(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core description."""
        self._filters[SearchField.PROXY_DC_DESCRIPTION] = value
        return self

    def dc_format(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core format."""
        self._filters[SearchField.PROXY_DC_FORMAT] = value
        return self

    def dc_identifier(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core identifier."""
        self._filters[SearchField.PROXY_DC_IDENTIFIER] = value
        return self

    def language(self, value: str) -> "QueryBuilder":
        """Filter by language."""
        self._filters[SearchField.LANGUAGE] = value
        return self

    def dc_publisher(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core publisher."""
        self._filters[SearchField.PROXY_DC_PUBLISHER] = value
        return self

    def dc_rights(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core rights."""
        self._filters[SearchField.PROXY_DC_RIGHTS] = value
        return self

    def dc_source(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core source."""
        self._filters[SearchField.PROXY_DC_SOURCE] = value
        return self

    def dc_subject(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core subject."""
        self._filters[SearchField.PROXY_DC_SUBJECT] = value
        return self

    def dc_title(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core title."""
        self._filters[SearchField.PROXY_DC_TITLE] = value
        return self

    def dc_type(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core type."""
        self._filters[SearchField.PROXY_DC_TYPE] = value
        return self

    def dc_type_search(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core type search field."""
        self._filters[SearchField.PROXY_DC_TYPE_SEARCH] = value
        return self

    def dcterms_alternative(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core Terms alternative title."""
        self._filters[SearchField.PROXY_DCTERMS_ALTERNATIVE] = value
        return self

    def dcterms_created(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core Terms created date."""
        self._filters[SearchField.PROXY_DCTERMS_CREATED] = value
        return self

    def dcterms_has_part(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core Terms hasPart relation."""
        self._filters[SearchField.PROXY_DCTERMS_HASPART] = value
        return self

    def dcterms_is_part_of(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core Terms isPartOf relation."""
        self._filters[SearchField.PROXY_DCTERMS_ISPARTOF] = value
        return self

    def dcterms_issued(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core Terms issued date."""
        self._filters[SearchField.PROXY_DCTERMS_ISSUED] = value
        return self

    def dcterms_medium(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core Terms medium."""
        self._filters[SearchField.PROXY_DCTERMS_MEDIUM] = value
        return self

    def dcterms_provenance(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core Terms provenance."""
        self._filters[SearchField.PROXY_DCTERMS_PROVENANCE] = value
        return self

    def dcterms_spatial(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core Terms spatial coverage."""
        self._filters[SearchField.PROXY_DCTERMS_SPATIAL] = value
        return self

    def dcterms_temporal(self, value: str) -> "QueryBuilder":
        """Filter by Dublin Core Terms temporal coverage."""
        self._filters[SearchField.PROXY_DCTERMS_TEMPORAL] = value
        return self

    def edm_current_location(self, value: str) -> "QueryBuilder":
        """Filter by EDM current location."""
        self._filters[SearchField.PROXY_EDM_CURRENTLOCATION] = value
        return self

    def edm_has_met(self, value: str) -> "QueryBuilder":
        """Filter by EDM hasMet relation."""
        self._filters[SearchField.PROXY_EDM_HASMET] = value
        return self

    def edm_is_related_to(self, value: str) -> "QueryBuilder":
        """Filter by EDM isRelatedTo relation."""
        self._filters[SearchField.PROXY_EDM_ISRELATEDTO] = value
        return self

    def type_filter(self, value: str) -> "QueryBuilder":
        """Filter by media type (TYPE field)."""
        self._filters[SearchField.TYPE] = value
        return self

    def year_filter(self, value: str) -> "QueryBuilder":
        """Filter by year."""
        self._filters[SearchField.YEAR] = value
        return self

    def data_provider(self, value: str) -> "QueryBuilder":
        """Filter by data provider."""
        self._filters[SearchField.DATA_PROVIDER] = value
        return self

    def provider_edm_has_view(self, value: str) -> "QueryBuilder":
        """Filter by provider aggregation EDM hasView."""
        self._filters[SearchField.PROVIDER_AGGREGATION_EDM_HASVIEW] = value
        return self

    def provider_edm_intermediate_provider(self, value: str) -> "QueryBuilder":
        """Filter by provider aggregation EDM intermediate provider."""
        self._filters[SearchField.PROVIDER_AGGREGATION_EDM_INTERMEDIATEPROVIDER] = value
        return self

    def provider_edm_is_shown_at(self, value: str) -> "QueryBuilder":
        """Filter by provider aggregation EDM isShownAt."""
        self._filters[SearchField.PROVIDER_AGGREGATION_EDM_ISSHOWNAT] = value
        return self

    def provider_edm_is_shown_by(self, value: str) -> "QueryBuilder":
        """Filter by provider aggregation EDM isShownBy."""
        self._filters[SearchField.PROVIDER_AGGREGATION_EDM_ISSHOWNBY] = value
        return self

    def provider_edm_object(self, value: str) -> "QueryBuilder":
        """Filter by provider aggregation EDM object."""
        self._filters[SearchField.PROVIDER_AGGREGATION_EDM_OBJECT] = value
        return self

    def provider(self, value: str) -> "QueryBuilder":
        """Filter by provider."""
        self._filters[SearchField.PROVIDER] = value
        return self

    def provider_dc_rights(self, value: str) -> "QueryBuilder":
        """Filter by provider aggregation DC rights."""
        self._filters[SearchField.PROVIDER_AGGREGATION_DC_RIGHTS] = value
        return self

    def rights(self, value: str) -> "QueryBuilder":
        """Filter by rights."""
        self._filters[SearchField.RIGHTS] = value
        return self

    def ugc(self, value: bool) -> "QueryBuilder":
        """Filter by user generated content flag."""
        self._filters[SearchField.UGC] = str(value).lower()
        return self

    def edm_preview_no_distribute(self, value: bool) -> "QueryBuilder":
        """Filter by EDM preview no distribute flag."""
        self._filters[SearchField.EDM_PREVIEWNODISTRIBUTE] = str(value).lower()
        return self

    def collection_name(self, value: str) -> "QueryBuilder":
        """Filter by Europeana collection name."""
        self._filters[SearchField.EUROPEANA_COLLECTIONNAME] = value
        return self

    def dataset_name(self, value: str) -> "QueryBuilder":
        """Filter by EDM dataset name."""
        self._filters[SearchField.EDM_DATASETNAME] = value
        return self

    def country(self, value: str) -> "QueryBuilder":
        """Filter by country."""
        self._filters[SearchField.COUNTRY] = value
        return self

    def aggregation_language(self, value: str) -> "QueryBuilder":
        """Filter by Europeana aggregation EDM language."""
        self._filters[SearchField.EUROPEANA_AGGREGATION_EDM_LANGUAGE] = value
        return self

    def web_resource(self, value: str) -> "QueryBuilder":
        """Filter by EDM web resource."""
        self._filters[SearchField.EDM_WEBRESOURCE] = value
        return self

    def web_resource_rights(self, value: str) -> "QueryBuilder":
        """Filter by web resource DC rights."""
        self._filters[SearchField.WR_DC_RIGHTS] = value
        return self

    def web_resource_is_referenced_by(self, value: str) -> "QueryBuilder":
        """Filter by web resource DCTERMS isReferencedBy."""
        self._filters[SearchField.WR_DCTERMS_ISREFERENCEDBY] = value
        return self

    def web_resource_next_in_sequence(self, value: str) -> "QueryBuilder":
        """Filter by web resource EDM isNextInSequence."""
        self._filters[SearchField.WR_EDM_ISNEXTINSEQUENCE] = value
        return self

    def web_resource_edm_rights(self, value: str) -> "QueryBuilder":
        """Filter by web resource EDM rights."""
        self._filters[SearchField.WR_EDM_RIGHTS] = value
        return self

    def web_resource_has_service(self, value: str) -> "QueryBuilder":
        """Filter by web resource SVCS hasService."""
        self._filters[SearchField.WR_SVCS_HASSERVICE] = value
        return self

    def web_resource_cc_license(self, value: str) -> "QueryBuilder":
        """Filter by web resource CC license."""
        self._filters[SearchField.WR_CC_LICENSE] = value
        return self

    def provider_cc_license(self, value: str) -> "QueryBuilder":
        """Filter by provider aggregation CC license."""
        self._filters[SearchField.PROVIDER_AGGREGATION_CC_LICENSE] = value
        return self

    def provider_odrl_inherited_from(self, value: str) -> "QueryBuilder":
        """Filter by provider aggregation ODRL inherited from."""
        self._filters[SearchField.PROVIDER_AGGREGATION_ODRL_INHERITED_FROM] = value
        return self

    def web_resource_odrl_inherited_from(self, value: str) -> "QueryBuilder":
        """Filter by web resource CC ODRL inherited from."""
        self._filters[SearchField.WR_CC_ODRL_INHERITED_FROM] = value
        return self

    def web_resource_cc_deprecated_on(self, value: str) -> "QueryBuilder":
        """Filter by web resource CC deprecated on date."""
        self._filters[SearchField.WR_CC_DEPRECATED_ON] = value
        return self

    def provider_cc_deprecated_on(self, value: str) -> "QueryBuilder":
        """Filter by provider aggregation CC deprecated on date."""
        self._filters[SearchField.PROVIDER_AGGREGATION_CC_DEPRECATED_ON] = value
        return self

    def service(self, value: str) -> "QueryBuilder":
        """Filter by SVCS service."""
        self._filters[SearchField.SVCS_SERVICE] = value
        return self

    def service_conforms_to(self, value: str) -> "QueryBuilder":
        """Filter by service DCTERMS conformsTo."""
        self._filters[SearchField.SV_DCTERMS_CONFORMSTO] = value
        return self

    def agent(self, value: str) -> "QueryBuilder":
        """Filter by EDM agent."""
        self._filters[SearchField.EDM_AGENT] = value
        return self

    def agent_pref_label(self, value: str) -> "QueryBuilder":
        """Filter by agent SKOS preferred label."""
        self._filters[SearchField.AG_SKOS_PREFLABEL] = value
        return self

    def agent_alt_label(self, value: str) -> "QueryBuilder":
        """Filter by agent SKOS alternative label."""
        self._filters[SearchField.AG_SKOS_ALTLABEL] = value
        return self

    def agent_name(self, value: str) -> "QueryBuilder":
        """Filter by agent FOAF name."""
        self._filters[SearchField.AG_FOAF_NAME] = value
        return self

    def agent_birth_date(self, value: str) -> "QueryBuilder":
        """Filter by agent RDA GR2 date of birth."""
        self._filters[SearchField.AG_RDAGR2_DATEOFBIRTH] = value
        return self

    def agent_death_date(self, value: str) -> "QueryBuilder":
        """Filter by agent RDA GR2 date of death."""
        self._filters[SearchField.AG_RDAGR2_DATEOFDEATH] = value
        return self

    def agent_birth_place(self, value: str) -> "QueryBuilder":
        """Filter by agent RDA GR2 place of birth."""
        self._filters[SearchField.AG_RDAGR2_PLACEOFBIRTH] = value
        return self

    def agent_death_place(self, value: str) -> "QueryBuilder":
        """Filter by agent RDA GR2 place of death."""
        self._filters[SearchField.AG_RDAGR2_PLACEOFDEATH] = value
        return self

    def agent_profession(self, value: str) -> "QueryBuilder":
        """Filter by agent RDA GR2 profession or occupation."""
        self._filters[SearchField.AG_RDAGR2_PROFESSIONOROCCUPATION] = value
        return self

    def concept(self, value: str) -> "QueryBuilder":
        """Filter by SKOS concept."""
        self._filters[SearchField.SKOS_CONCEPT] = value
        return self

    def concept_pref_label(self, value: str) -> "QueryBuilder":
        """Filter by concept SKOS preferred label."""
        self._filters[SearchField.CC_SKOS_PREFLABEL] = value
        return self

    def concept_alt_label(self, value: str) -> "QueryBuilder":
        """Filter by concept SKOS alternative label."""
        self._filters[SearchField.CC_SKOS_ALTLABEL] = value
        return self

    def place(self, value: str) -> "QueryBuilder":
        """Filter by EDM place."""
        self._filters[SearchField.EDM_PLACE] = value
        return self

    def place_latitude(self, value: str) -> "QueryBuilder":
        """Filter by place WGS84 latitude."""
        self._filters[SearchField.PL_WGS84_POS_LAT] = value
        return self

    def place_longitude(self, value: str) -> "QueryBuilder":
        """Filter by place WGS84 longitude."""
        self._filters[SearchField.PL_WGS84_POS_LONG] = value
        return self

    def place_altitude(self, value: str) -> "QueryBuilder":
        """Filter by place WGS84 altitude."""
        self._filters[SearchField.PL_WGS84_POS_ALT] = value
        return self

    def place_pref_label(self, value: str) -> "QueryBuilder":
        """Filter by place SKOS preferred label."""
        self._filters[SearchField.PL_SKOS_PREFLABEL] = value
        return self

    def place_alt_label(self, value: str) -> "QueryBuilder":
        """Filter by place SKOS alternative label."""
        self._filters[SearchField.PL_SKOS_ALTLABEL] = value
        return self

    def timespan(self, value: str) -> "QueryBuilder":
        """Filter by EDM timespan."""
        self._filters[SearchField.EDM_TIMESPAN] = value
        return self

    def timespan_pref_label(self, value: str) -> "QueryBuilder":
        """Filter by timespan SKOS preferred label."""
        self._filters[SearchField.TS_SKOS_PREFLABEL] = value
        return self

    def timespan_alt_label(self, value: str) -> "QueryBuilder":
        """Filter by timespan SKOS alternative label."""
        self._filters[SearchField.TS_SKOS_ALTLABEL] = value
        return self

    def text_query(self, query: str) -> "QueryBuilder":
        """Add free text search query."""
        self._text_query = query
        return self

    def geographic(self, lat: float, lon: float, radius_km: float) -> "QueryBuilder":
        """Add geographic proximity search."""
        self._geographic = (lat, lon, radius_km)
        return self

    def facets(self, *field_names: Union[str, SearchField]) -> "QueryBuilder":
        """Add facet fields for aggregated results. Fields must be facetable."""
        for field in field_names:
            # With StrEnum, we can use the field directly since it's a string
            field_str = str(
                field
            )  # Works for both str and SearchField (which IS a str)
            if field_str not in FACETABLE_FIELDS:
                raise ValueError(
                    f"Field '{field_str}' is not facetable. Valid facetable fields: {FACETABLE_FIELDS}"
                )
            self._facets.append(field_str)
        return self

    def profile(self, profile: Union[str, Profile]) -> "QueryBuilder":
        """Set response detail level."""
        self._profile = profile
        return self

    def rows(self, count: int) -> "QueryBuilder":
        """Set number of results per page."""
        self._rows = min(count, MAX_ROWS)
        return self

    def reusability(self, level: Union[str, Reusability]) -> "QueryBuilder":
        """Set reusability filter."""
        self._reusability = level
        return self

    def with_media(self, has_media: bool = True) -> "QueryBuilder":
        """Filter items with/without media."""
        self._media_flag = has_media
        return self

    def with_thumbnails(self, has_thumbnails: bool = True) -> "QueryBuilder":
        """Filter items with/without thumbnails."""
        self._thumbnail_flag = has_thumbnails
        return self

    def get_query_string(self) -> str:
        """Generate and return the Lucene query string."""
        return build_query_string(self._text_query, self._filters)

    def __repr__(self) -> str:
        """String representation for debugging."""
        parts = []
        if self._text_query:
            parts.append(f"text='{self._text_query}'")
        if self._filters:
            filter_strs = [f"{k}:{v}" for k, v in self._filters.items()]
            parts.append(f"filters=[{', '.join(filter_strs)}]")
        if self._geographic:
            lat, lon, radius = self._geographic
            parts.append(f"geographic=({lat}, {lon}, {radius}km)")
        return f"QueryBuilder({', '.join(parts)})"


class EuropeanaClient:
    """Client for interacting with the Europeana Search API."""

    DEFAULT_BASE_URL = "https://api.europeana.eu/record/v2/search.json"

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the Europeana client.

        Args:
            api_key: Your Europeana API key
            base_url: Optional custom base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self._client = httpx.Client(timeout=30.0)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close HTTP client."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def search_raw(
        self,
        query: QueryBuilder,
        cursor: str = "*",
        **kwargs,
    ) -> SearchResults:
        """
        Perform a search on the Europeana API.

        Args:
            query: QueryBuilder object with search parameters
            cursor: Pagination cursor (use "*" for first page)
            **kwargs: Additional query parameters to override

        Returns:
            SearchResults object containing raw items and pagination info
        """
        # Get query string from QueryBuilder
        query_str = query.get_query_string()

        # Extract parameters from QueryBuilder
        rows = query._rows
        facets = query._facets if query._facets else None
        profile = query._profile
        geographic = query._geographic
        reusability = query._reusability
        media = query._media_flag
        thumbnail = query._thumbnail_flag

        # Handle enum values
        if isinstance(profile, Profile):
            profile = profile.value
        if isinstance(reusability, Reusability):
            reusability = reusability.value

        # Prepare parameters
        params = {
            "query": query_str or "*:*",
            "rows": str(min(rows, MAX_ROWS)),
            "cursor": cursor,
            "wskey": self.api_key,
            "profile": profile,
        }

        # Add facets if requested
        if facets:
            params["facet"] = ",".join(facets)

        # Add geographic filter if provided
        if geographic:
            lat, lon, radius = geographic
            params["qf"] = f"distance(coverageLocation,{lat},{lon},{radius})"

        # Add reusability filter
        if reusability:
            params["reusability"] = reusability

        # Add media filters
        if media is not None:
            params["media"] = str(media).lower()
        if thumbnail is not None:
            params["thumbnail"] = str(thumbnail).lower()

        # Add any additional parameters
        params.update(kwargs)

        # Make the request
        response = self._client.get(self.base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract results
        return SearchResults(
            items=data.get("items", []),
            total_results=data.get("totalResults", 0),
            next_cursor=data.get("nextCursor"),
            facets=data.get("facets", []) if facets else None,
            query=query_str,
        )

    def search(
        self,
        query: QueryBuilder,
        cursor: str = "*",
        **kwargs,
    ) -> StructuredSearchResults:
        """
        Perform a search on the Europeana API with structured results.

        Args:
            query: QueryBuilder object with search parameters
            cursor: Pagination cursor (use "*" for first page)
            **kwargs: Additional query parameters to override

        Returns:
            StructuredSearchResults object with parsed EuropeanaItem instances
        """
        # Get the raw search results
        raw_results = self.search_raw(query, cursor, **kwargs)

        # Convert to structured results
        return StructuredSearchResults.from_search_results(raw_results)

    def search_all_raw(
        self,
        query: QueryBuilder,
        max_records: Optional[int] = None,
    ) -> Iterator[Dict]:
        """
        Iterator that fetches all results for a query using pagination, returning raw JSON data.

        Args:
            query: QueryBuilder object with search parameters
            max_records: Maximum number of records to fetch (None for all)

        Yields:
            Individual raw Dict items from all result pages
        """
        cursor = "*"
        records_fetched = 0

        while True:
            # Calculate rows for this request
            if max_records:
                remaining = max_records - records_fetched
                if remaining <= 0:
                    break
                rows = min(DEFAULT_ROWS, remaining)
            else:
                rows = DEFAULT_ROWS

            # Create a copy of the query with the current page size
            page_query = copy.deepcopy(query)
            page_query._rows = rows

            # Fetch a page of results
            results = self.search_raw(page_query, cursor=cursor)

            # Yield items from this page
            for item in results.items:
                yield item
                records_fetched += 1
                if max_records and records_fetched >= max_records:
                    return

            # Check if there are more pages
            if not results.next_cursor or len(results.items) == 0:
                break

            cursor = results.next_cursor

    def search_all(
        self,
        query: QueryBuilder,
        max_records: Optional[int] = None,
    ) -> Iterator[EuropeanaItem]:
        """
        Iterator that fetches all results for a query using pagination, returning structured items.

        Args:
            query: QueryBuilder object with search parameters
            max_records: Maximum number of records to fetch (None for all)

        Yields:
            EuropeanaItem: Parsed item instances instead of raw dictionaries

        Example:
            client = EuropeanaClient(api_key)
            query = client.query().creator("Van Gogh").media_type(MediaType.IMAGE)

            for item in client.search_all(query, max_records=100):
                print(f"Title: {item.get_first_title()}")
                print(f"Creator: {item.get_first_creator()}")
        """
        cursor = "*"
        records_fetched = 0

        while True:
            # Calculate rows for this request
            if max_records:
                remaining = max_records - records_fetched
                if remaining <= 0:
                    break
                rows = min(DEFAULT_ROWS, remaining)
            else:
                rows = DEFAULT_ROWS

            # Create a copy of the query with the current page size
            page_query = copy.deepcopy(query)
            page_query._rows = rows

            # Fetch a page of structured results
            results = self.search(page_query, cursor=cursor)

            # Yield items from this page
            for item in results.items:
                yield item
                records_fetched += 1
                if max_records and records_fetched >= max_records:
                    return

            # Check if there are more pages
            if not results.next_cursor or len(results.items) == 0:
                break

            cursor = results.next_cursor

    def get_place_entity(self, entity_uri: str) -> PlaceEntity:
        """
        Retrieve a place entity from the Europeana Entity API.

        Args:
            entity_uri: Either a full URI (http://data.europeana.eu/place/92)
                       or entity path (place/92)

        Returns:
            PlaceEntity: The retrieved place entity with all metadata

        Raises:
            httpx.HTTPStatusError: If the entity is not found or API error occurs
            ValueError: If the entity URI format is invalid
        """
        # Extract entity path from full URI if needed
        entity_path = self._extract_entity_path(entity_uri)

        # Construct the Entity API URL
        entity_url = f"https://api.europeana.eu/entity/{entity_path}"

        params = {"wskey": self.api_key}
        headers = {"Accept": "application/json"}

        response = self._client.get(entity_url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        return PlaceEntity.from_dict(data)

    def is_place_entity_uri(self, uri: str) -> bool:
        """
        Check if a string is a valid place entity URI.

        Args:
            uri: String to check

        Returns:
            bool: True if the string is a valid place entity URI, False otherwise
        """
        if not uri or not isinstance(uri, str):
            return False

        # Check for full Europeana place URI pattern
        if uri.startswith("http://data.europeana.eu/place/"):
            # Ensure there's an ID after the path
            place_id = uri.replace("http://data.europeana.eu/place/", "")
            return bool(place_id.strip())

        # Check for path format (place/id)
        if uri.startswith("place/"):
            # Ensure there's an ID after "place/"
            place_id = uri.replace("place/", "")
            return bool(place_id.strip())

        return False

    def get_place_entities_from_atribute(
        self, uri_list: str | List[str]
    ) -> Tuple[List[PlaceEntity], Dict[str, str], List[str]]:
        """
        Process a list of strings and retrieve place entities for valid place URIs.

        Args:
            uri_list: List of strings to process

        Returns:
            Tuple containing:
            - List of successfully retrieved PlaceEntity objects
            - Dictionary mapping failed URIs to their error messages
            - List of strings that weren't recognized as place URIs
        """
        place_entities = []
        failed_uris = {}
        non_place_strings = []

        # Normalize input to a list
        if isinstance(uri_list, str):
            uri_list = [uri_list]

        for uri in uri_list:
            if not isinstance(uri, str):
                non_place_strings.append(str(uri))
                continue

            if self.is_place_entity_uri(uri):
                try:
                    place_entity = self.get_place_entity(uri)
                    place_entities.append(place_entity)
                except Exception as e:
                    failed_uris[uri] = str(e)
            else:
                non_place_strings.append(uri)

        return place_entities, failed_uris, non_place_strings

    def _extract_entity_path(self, entity_uri: str) -> str:
        """Extract entity path from full URI or validate path format."""
        # If it's a full URI, extract the path
        if entity_uri.startswith("http://data.europeana.eu/"):
            # Extract everything after the domain
            match = re.match(r"http://data\.europeana\.eu/(.+)", entity_uri)
            if match:
                return match.group(1)
            else:
                raise ValueError(f"Invalid Europeana entity URI format: {entity_uri}")

        # If it looks like a path (contains /), use as-is
        if "/" in entity_uri:
            return entity_uri

        # Otherwise, assume it's malformed
        raise ValueError(f"Invalid entity URI or path format: {entity_uri}")

    def query(self) -> QueryBuilder:
        """Create a new QueryBuilder for fluent query construction."""
        return QueryBuilder()
