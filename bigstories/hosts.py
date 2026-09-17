from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'www', 'main.urls', name='www'),
    host(r'dash', 'dash.urls', name='dash'),
    host(r'editors', 'editor.urls', name='editors'),
    host(r'content', 'content.urls', name='content'),
    host(r'management', 'management.urls', name='management'),
    host(r'business', 'business.urls', name='business'),
    host(r'', 'main.urls', name='main'),        # bare domain — must be LAST
)