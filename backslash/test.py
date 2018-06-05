from sentinels import NOTHING

from .api_object import APIObject
from .commentable import Commentable
from .error_container import ErrorContainer
from .related_entity_container import RelatedEntityContainer
from .warning_container import WarningContainer
from .lazy_query import LazyQuery
from .metadata_holder import MetadataHolder
from .timing_container import TimingContainer
import slash

_UPDATE_PARAMETERS_FUNC = 'update_test_parameters'

class Test(APIObject, MetadataHolder, ErrorContainer, WarningContainer, Commentable, RelatedEntityContainer, TimingContainer):

    @property
    def ui_url(self):
        return self.client.get_ui_url('sessions/{}/tests/{}'.format(self.session_display_id, self.logical_id or self.id))

    def report_end(self, duration=NOTHING):
        self.client.api.call_function('report_test_end', {'id': self.id, 'duration': duration})

    def mark_skipped(self, reason=None):
        self.client.api.call_function('report_test_skipped', {'id': self.id, 'reason': reason})

    def report_interrupted(self):
        self.client.api.call_function('report_test_interrupted', {'id': self.id})

    def update_parameters(self):
        variation = getattr(slash.context.test.__slash__, 'variation', None)
        if not variation or not _UPDATE_PARAMETERS_FUNC in self.client.api.info().endpoints:
            return
        updated_param_names = variation.get_computed_parameter_names()
        if updated_param_names:
            self.client.api.call_function(_UPDATE_PARAMETERS_FUNC,
                                          {
                                           'test_id': self.id,
                                           'parameters': {param_name: variation.values[param_name] for param_name in updated_param_names}
                                          })

    def query_errors(self):
        """Queries tests of the current session

        :rtype: A lazy query object
        """
        return LazyQuery(self.client, '/rest/errors', query_params={'test_id': self.id})

    def get_session(self):
        return self.client.api.get('/rest/sessions/{0}'.format(self.session_id))

    def get_parent(self):
        return self.get_session()

    def update_status_description(self, description):
        return self.client.api.call_function('update_status_description', {'test_id': self.id, 'description': description})
