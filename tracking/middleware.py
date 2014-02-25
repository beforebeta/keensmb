import re
import logging
from datetime import datetime

from django.db import DatabaseError
from django.utils.timezone import now

from tracking.models import Visitor


logger = logging.getLogger(__name__)

SESSION_VAR_NAME = 'visitor'


class VisitorMiddleware(object):
    def process_request(self, request):
        if SESSION_VAR_NAME not in request.session:
            visitor = get_visitor(request)
            request.session[SESSION_VAR_NAME] = visitor.id
            request.session.modified = True


def get_visitor(request):
    """Extract visitor tracking information from Google Analytics cookie and
    use that to create Visitor object.
    """
    current_time = now()

    visitor = Visitor(
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        referrer=request.META.get('HTTP_REFERER', ''),
        first_visit=current_time,
        last_visit=current_time,
        visits=1,
    )

    # extract visits information from GA cookies
    cookie = request.COOKIES.get('__utma')
    if cookie:
        try:
            first_visit, last_visit, current_visit, visits = map(int, cookie.split('.', 5)[2:6])
            first_visit, last_visit = map(datetime.fromtimestamp, (first_visit, last_visit))
        except (ValueError, IndexError):
            logger.error('Failed to extrect tracking information from GA cookie {0!r}'.format(
                cookie))
        else:
            visitor.first_visit = first_visit
            visitor.last_visit = last_visit
            visitor.visits = visits

    # get acquisition source information
    cookie = request.COOKIES.get('__utmz')
    if cookie:
        try:
            data = cookie.split('.', 4)[-1]
            data = dict(match.groups() for match in re.finditer(
                r'(utm(?:csr|ccn|cmd|ctr))=([^\|]*)', data))
        except (ValueError, IndexError):
            logger.error('Malformed GA cookie: {0!r}'.format(cookie))
        else:
            visitor.source = normalize_ga_value(data.get('utmcsr'))
            visitor.medium = normalize_ga_value(data.get('utmcmd'))
            visitor.campaign = normalize_ga_value(data.get('utmccn'))
            visitor.keywords = normalize_ga_value(data.get('utm.ctr'))

    for param, attr in (
        ('utm_source', 'source'),
        ('utm_medium', 'medium'),
        ('utm_campaign', 'campaign'),
        ('utm_term', 'keywords'),
    ):
        if not getattr(visitor, attr):
            setattr(visitor, attr, request.GET.get(param, 'direct'))
    try:
        visitor.save()
    except DatabaseError:
        logger.exception('Failed to save visitor')

    return visitor


def normalize_ga_value(value):
    return {
        '(direct)': 'direct',
        '(none)': None,
        '(notset)': None,
    }.get(value, value)
