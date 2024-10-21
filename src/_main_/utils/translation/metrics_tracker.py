import threading
from _main_.utils.common import parse_datetime_to_aware
from _main_.utils.metrics import put_metric_data
from _main_.utils.utils import calc_string_list_length
from _main_.settings import EnvConfig

class TranslationMetrics:
    """
    A class to track and record various metrics related to language translation operations.
    Metrics are recorded on AWS CloudWatch.
    """

    def __init__(self):
        """
        Initializes the TranslationMetrics class with a namespace and a timestamp.
        """
        self.name_space = "LocalizationSystem"
        self.time_stamp = parse_datetime_to_aware()

    def record_metrics_on_cloudwatch(self, metric_data):
        """
        Records the given metric data on AWS CloudWatch.

        Args:
            metric_data (list): A list of dictionaries containing metric data to be recorded.
        """
        env_name_space = f"{EnvConfig.name.title()}/{self.name_space}"

        threading.Thread(target=put_metric_data, args=(env_name_space, metric_data)).start()

    def track_language_usage_count(self, destination_language):
        """
        Tracks the usage count of a specific language.

        Args:
            destination_language (str): The language code of the destination language.
        """
        metric_data = [
            {
                'MetricName': "LanguageUsageCount",
                'Dimensions': [
                    {
                        'Name': 'Language',
                        'Value': destination_language
                    },
                ],
                "Value": 1,
                'Unit': 'Count',
                'Timestamp': self.time_stamp,
            },
        ]
        self.record_metrics_on_cloudwatch(metric_data)

    def track_language_usage_per_site(self, destination_language, site_id):
        """
        Tracks the usage of a language per URL to determine which site or campaign is mostly viewed in a specific language.

        Args:
            destination_language (str): The language code of the destination language.
            url (str): The URL where the language is used.
        """
        metric_data = [
            {
                'MetricName': "LanguageUsagePerSite",
                'Dimensions': [
                    {
                        'Name': 'Language',
                        'Value': destination_language
                    },
                    {
                        'Name': 'SiteID',
                        'Value': site_id
                    },
                ],
                "Value": 1,
                'Unit': 'Count',
                'Timestamp': self.time_stamp,
            },
        ]
        self.record_metrics_on_cloudwatch(metric_data)

    def track_translation_latency(self, source_language, target_language, duration):
        """
        Tracks the latency (how long it takes to translate content from one language to another) of a translation operation and records the metric on CloudWatch.

        Args:
            source_language (str): The language code of the source text.
            target_language (str): The language code of the target text.
            duration (float): The duration of the translation operation in seconds.
        """
        metric_data = [
            {
                'MetricName': "TranslationLatency",
                'Dimensions': [
                    {
                        'Name': 'SourceLanguage',
                        'Value': source_language,
                    },
                    {
                        'Name': 'TargetLanguage',
                        'Value': target_language,
                    },
                ],
                "Value": duration,
                'Unit': 'Milliseconds',
                'Timestamp': self.time_stamp,
            },
        ]
        self.record_metrics_on_cloudwatch(metric_data)

    def track_error_rate(self, source_language, target_language):
        """
        Tracks the error rate of translations between the specified source and target languages.

        Args:
            source_language (str): The language code of the source language.
            target_language (str): The language code of the target language.
        """
        metric_data = [
            {
                'MetricName': "TranslationErrorRate",
                'Dimensions': [
                    {
                        'Name': 'SourceLanguage',
                        'Value': source_language,
                    },
                    {
                        'Name': 'TargetLanguage',
                        'Value': target_language,
                    },
                ],
                "Value": 1,
                'Unit': 'Count',
                'Timestamp': self.time_stamp,
            },
        ]
        self.record_metrics_on_cloudwatch(metric_data)