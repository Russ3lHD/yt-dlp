from .common import InfoExtractor
from ..utils import (
    int_or_none,
    try_get,
)


class TwentyMinutenIE(InfoExtractor):
    IE_NAME = '20min'
    _VALID_URL = r'''(?x)
        https?://(?:www\.)?20min\.ch/
        (?:
            videotv/?\?.*?\bvid=(?P<id1>\d+)
            |videoplayer/videoplayer\.html\?.*?\bvideoId@(?P<id2>\d+)
            |story/[^/?#]+-(?P<id3>\d+)
        )
    '''
    _EMBED_REGEX = [r'<iframe[^>]+src=(["\'])(?P<url>(?:(?:https?:)?//)?(?:www\.)?20min\.ch/videoplayer/videoplayer.html\?.*?\bvideoId@\d+.*?)\1']
    _TESTS = [{
        'url': 'http://www.20min.ch/videotv/?vid=469148&cid=2',
        'md5': 'e7264320db31eed8c38364150c12496e',
        'info_dict': {
            'id': '469148',
            'ext': 'mp4',
            'title': '85 000 Franken für 15 perfekte Minuten',
            'thumbnail': r're:https?://.*\.jpg$',
        },
    }, {
        'url': 'http://www.20min.ch/videoplayer/videoplayer.html?params=client@twentyDE|videoId@523629',
        'info_dict': {
            'id': '523629',
            'ext': 'mp4',
            'title': 'So kommen Sie bei Eis und Schnee sicher an',
            'description': 'md5:117c212f64b25e3d95747e5276863f7d',
            'thumbnail': r're:https?://.*\.jpg$',
        },
        'params': {
            'skip_download': True,
        },
    }, {
        'url': 'http://www.20min.ch/videotv/?cid=44&vid=468738',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        mobj = self._match_valid_url(url)
        video_id = mobj.group('id1') or mobj.group('id2') or mobj.group('id3')
        webpage = self._download_webpage(url, video_id)

        # Try to find iframe with video player
        iframe_url = self._search_regex(
            r'<iframe[^>]+src=["\']([^"\']*videoplayer\.html[^"\']+)["\']',
            webpage, 'iframe video player', default=None)
        video_url = None
        if iframe_url:
            # Download the iframe page and extract video src
            iframe_webpage = self._download_webpage(iframe_url, video_id, note='Downloading iframe player')
            video_url = self._search_regex(
                r'<video[^>]+src=["\']([^"\']+)["\']', iframe_webpage, 'video url', default=None)

        if not video_url:
            # Fallback: try to find video src in main page
            video_url = self._search_regex(
                r'<video[^>]+src=["\']([^"\']+)["\']', webpage, 'video url', default=None)


        if not video_url:
            # Fallback: look for url_high in JSON
            video_url = self._search_regex(
                r'"url_high"\s*:\s*"(https?://[^"]+)"', webpage, 'high quality video url', default=None)

        if not video_url:
            raise self.raise_no_formats('Unable to extract video url')

        title = self._og_search_title(webpage, default=video_id)

        formats = [{
            'url': video_url,
            'ext': 'mp4',
            'format_id': 'http',
        }]

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
        }

