from office365.runtime.odata.odata_json_format import ODataJsonFormat


class V4JsonFormat(ODataJsonFormat):
    """V4 JSON format"""

    def __init__(self, metadata_level):
        super(V4JsonFormat, self).__init__(metadata_level)
        """The IEEE754Compatible format parameter indicates that the service MUST serialize Edm.Int64 and
        Edm.Decimal numbers as strings."""
        self.IEEE754Compatible = False
        """"""
        self.streaming = False
        self.collection_tag_name = "value"
        self.metadata_type_tag_name = "@odata.type"

    def get_media_type(self):
        return "application/json;odata.metadata={0};odata.streaming={1};IEEE754Compatible={2}" \
            .format(self.metadata_level, self.streaming, self.IEEE754Compatible)
