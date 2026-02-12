import requests
from elastalert.alerts import Alerter, BasicMatchString
from elastalert.util import EAException

class WebhookAlerter(Alerter):
    required_options = frozenset(['webhook_url'])

    def __init__(self, *args):
        super(WebhookAlerter, self).__init__(*args)
        self.webhook_url = self.rule['webhook_url']

    def alert(self, matches):
        headers = {'Content-Type': 'application/json'}
        payload = {'matches': matches}
        try:
            response = requests.post(self.webhook_url, json=payload, headers=headers)
            response.raise_for_status()
        except Exception as e:
            raise EAException(f"Error sending webhook: {e}")

    def get_info(self):
        return {'type': 'webhook', 'webhook_url': self.webhook_url}
