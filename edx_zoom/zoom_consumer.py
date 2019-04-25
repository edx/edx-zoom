from __future__ import absolute_import, unicode_literals

import logging

from lti_consumer import LtiConsumerXBlock
from lti_consumer.utils import _
from web_fragments.fragment import Fragment
from xblock.core import List, Scope, String, XBlock
from xblock.fields import Boolean, Float, Integer
from xblockutils.resources import ResourceLoader

log = logging.getLogger(__name__)


class ZoomXBlock(LtiConsumerXBlock):
    launch_url = 'https://applications.zoom.us/lti/rich'
    lti_id = 'zoom'
    display_name = String(
        display_name=_("Display Name"),
        help=_(
            "Enter the name that students see for this component. "
            "Analytics reports may also use the display name to identify this component."
        ),
        scope=Scope.settings,
        default=_("Zoom"),
    )
    description = String(
        display_name=_("LTI Application Information"),
        help=_(
            "Enter a description of the third party application. "
            "If requesting username and/or email, use this text box to inform users "
            "why their username and/or email will be forwarded to a third party application."
        ),
        default=_("Use Zoom to join office hours and other fun meetings"),
        scope=Scope.settings
    )
    block_settings_key = 'edx_zoom'

    editable_fields = (
        'display_name', 'description', 'custom_parameters',
        'launch_target', 'inline_height', 'modal_height', 'modal_width'
    )


    @property
    def lti_provider_key_secret(self):
        """
        Obtains client_key and client_secret credentials from current course.
        """
        from .models import LTICredential
        creds = getattr(self, '_lti_credentials', None)
        if creds is None:
            log.info('getting key and secret for %s', self.course_id)
            try:
                cred = LTICredential.objects.get(course_id=self.course_id)
            except LTICredential.DoesNotExist:
                return None, None
            log.info('key:%s secret:%s', cred.key, cred.secret)
            creds = self._lti_credentials = cred.key, cred.secret
        return creds

    def _get_context_for_template(self):
        ctx = super(ZoomXBlock, self)._get_context_for_template()
        ctx['missing_credentials'] = self.lti_provider_key_secret[0] is None
        ctx['ask_to_send_username'] = ctx['ask_to_send_email'] = True
        return ctx

    def student_view(self, context):
        fragment = Fragment()
        lti_loader = ResourceLoader('lti_consumer')
        loader = ResourceLoader(__name__)
        context.update(self._get_context_for_template())
        fragment.add_content(loader.render_mako_template('/templates/student.html', context))
        fragment.add_css(loader.load_unicode('static/css/student.css'))
        fragment.add_javascript(lti_loader.load_unicode('static/js/xblock_lti_consumer.js'))
        fragment.initialize_js('LtiConsumerXBlock')
        return fragment
