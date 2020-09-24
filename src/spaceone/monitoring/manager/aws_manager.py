import logging

from spaceone.core.manager import BaseManager
from spaceone.monitoring.connector.aws_boto_connector import AWSBotoConnector

_LOGGER = logging.getLogger(__name__)


class AWSManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aws_connector: AWSBotoConnector = self.locator.get_connector('CloudTrailConnector')

    def verify(self, schema, options, secret_data):
        self.aws_connector.create_session(schema, options, secret_data)

    def list_logs(self, schema, options, secret_data, filters, resource, start, end, sort, limit=None):
        lookup_attributes, event_category, region_name = self._get_cloudtrail_query(resource)
        self.aws_connector.create_session(schema, options, secret_data, region_name)

        query = {
            'LookupAttributes': lookup_attributes,
            'StartTime': start,
            'EndTime': end,
        }

        if event_category:
            query.update({'EventCategory': event_category})

        if limit:
            query.update({'limit': limit})

        self.aws_connector.list_logs(**query)

    @staticmethod
    def _get_cloudtrail_query(resource):
        return resource.get('lookup_attributes'), \
               resource.get('event_category'), \
               resource.get('region_name', None)
