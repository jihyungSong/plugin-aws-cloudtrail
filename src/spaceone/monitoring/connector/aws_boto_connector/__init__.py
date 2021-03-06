import logging
import boto3

from spaceone.core import utils
from spaceone.core.connector import BaseConnector
from spaceone.monitoring.error import *
from spaceone.monitoring.connector.aws_boto_connector.cloudtrail import CloudTrail

__all__ = ['AWSBotoConnector']

_LOGGER = logging.getLogger(__name__)
DEFAULT_REGION_NAME = 'us-east-1'


class AWSBotoConnector(BaseConnector):

    def __init__(self, transaction, config):
        super().__init__(transaction, config)

    def create_session(self, schema, options: dict, secret_data: dict, region_name=None):
        self._check_secret_data(secret_data)

        aws_access_key_id = secret_data['aws_access_key_id']
        aws_secret_access_key = secret_data['aws_secret_access_key']
        role_arn = secret_data.get('role_arn')

        if region_name is None:
            region_name = secret_data.get('region_name', DEFAULT_REGION_NAME)

        if schema:
            getattr(self, f'_create_session_{schema}')(aws_access_key_id, aws_secret_access_key, region_name, role_arn)

    @staticmethod
    def _check_secret_data(secret_data):
        if 'aws_access_key_id' not in secret_data:
            raise ERROR_REQUIRED_PARAMETER(key='secret.aws_access_key_id')

        if 'aws_secret_access_key' not in secret_data:
            raise ERROR_REQUIRED_PARAMETER(key='secret.aws_secret_access_key')

    def _create_session_aws_access_key(self, aws_access_key_id, aws_secret_access_key, region_name, role_arn):
        self.session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key,
                                     region_name=region_name)

        sts = self.session.client('sts')
        sts.get_caller_identity()

    def _create_session_aws_assume_role(self, aws_access_key_id, aws_secret_access_key, region_name, role_arn):
        self._create_session_aws_access_key(aws_access_key_id, aws_secret_access_key, region_name, role_arn)

        sts = self.session.client('sts')
        assume_role_object = sts.assume_role(RoleArn=role_arn, RoleSessionName=utils.generate_id('AssumeRoleSession'))
        credentials = assume_role_object['Credentials']

        self.session = boto3.Session(aws_access_key_id=credentials['AccessKeyId'],
                                     aws_secret_access_key=credentials['SecretAccessKey'],
                                     region_name=region_name,
                                     aws_session_token=credentials['SessionToken'])

    def list_logs(self, **query):
        cloud_trail = CloudTrail(self.session)
        return cloud_trail.list_events(**query)
