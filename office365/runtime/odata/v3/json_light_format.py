from office365.runtime.odata.odata_json_format import ODataJsonFormat
from office365.runtime.odata.v3.metadata_level import ODataMetadataLevel


class JsonLightFormat(ODataJsonFormat):
    """JSON Light format for SharePoint Online/One Drive for Business"""

    def __init__(self, metadata_level=ODataMetadataLevel.Verbose):
        super(JsonLightFormat, self).__init__(metadata_level)
        if self.metadata_level == ODataMetadataLevel.Verbose:
            self.security_tag_name = "d"
            self.collection_tag_name = "results"
            self.collection_next_tag_name = "__next"
            self.metadata_type_tag_name = "__metadata"
            self.binding_parameter_tag_name = None
        else:
            self.collection_next_tag_name = "value"

    def get_media_type(self):
        return 'application/json;odata={0}'.format(self.metadata_level)

    @property
    def is_verbose(self):
        return self.metadata_level == ODataMetadataLevel.Verbose
