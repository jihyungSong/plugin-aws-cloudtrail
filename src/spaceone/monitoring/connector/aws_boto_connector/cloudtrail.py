import json
import logging

__all__ = ["CloudTrail"]


_LOGGER = logging.getLogger(__name__)
DEFAULT_REGION = 'us-east-1'

PAGINATOR_MAX_ITEMS = 10000
PAGINATOR_PAGE_SIZE = 50


class CloudTrail(object):

    def __init__(self, session):
        self.session = session
        self.client = self.session.client('cloudtrail')

    def list_events(self, **query):
        event_responses = []

        query = self._generate_query(is_paginate=True, **query)
        paginator = self.client.get_paginator('lookup_events')

        for events in paginator.paginate(**query):
            for event in events.get('Events', []):
                try:
                    event_string = event["CloudTrailEvent"]
                    detailed_event = self._parse_cloud_trail_event(event_string)
                    result = {'EventTime': event['EventTime'].isoformat(), 'AccessKeyId': event['AccessKeyId']}
                    result.update(detailed_event)
                    event_responses.append(result)

                except Exception as e:
                    print(f'[_lookup_events] error {e}')

        return event_responses

    @staticmethod
    def _parse_cloud_trail_event(cte):
        """ Parse CloudTrailEvent

        Args: CloudTrailEvent (raw data)
        Returns: dict
        """
        result = {}
        event = json.loads(cte)
        wanted_items = ['eventName', 'eventType', 'errorMessage']
        for item in wanted_items:
            if item in event:
                result[item] = event[item]

        return result

    @staticmethod
    def _generate_query(is_paginate=False, **query):
        if is_paginate:
            max_item = query.get('limit', PAGINATOR_MAX_ITEMS)

            query.update({
                'PaginationConfig': {
                    'MaxItems': max_item,
                    'PageSize': PAGINATOR_PAGE_SIZE
                }
            })

            if 'limit' in query:
                del query['limit']

        return query
