from django.conf import settings
from html.parser import HTMLParser


def settings_constants(request=None):
  return dict(
      DEBUG=settings.DEBUG,
      STAGING=settings.STAGING,
      DEMO=settings.DEMO,
      DEFAULT_FROM_EMAIL=settings.DEFAULT_FROM_EMAIL,
      ENV=settings.ENV,
      ENV_COLOR=settings.ENV_COLOR,
      SITE_URL=settings.SITE_URL,
      STRIPE_PUBLISHABLE_KEY=settings.STRIPE_PUBLISHABLE_KEY,
      SUPPORT_URL=settings.SUPPORT_URL,
      REACT_APP_SERVER=settings.REACT_APP_SERVER,
      GOOGLE_SIGNIN_CLIENT_ID=settings.GOOGLE_SIGNIN_CLIENT_ID,
  )


class IndexHtmlParser(HTMLParser):
  def __init__(self):
    super().__init__()
    self.script_urls = []
    self.manifest_url = ""

  def handle_starttag(self, tag, attrs):
    link_rel = None
    link_href = None
    for attr_name, attr_value in attrs:
      if tag == "script" and attr_name == "src":
        self.script_urls.append(attr_value)
      if tag == "link" and attr_name == "rel":
        link_rel = attr_value
      if tag == "link" and attr_name == "href":
        link_href = attr_value
    if link_rel == "manifest":
      self.manifest_url = link_href


def newlook_constants(request=None):
  if settings.REACT_APP_SERVER:
    script_urls = [("%s/%s.js" % (settings.REACT_APP_SERVER, path))
                   for path in ["reactBoilerplateDeps.dll", "main"]]
    manifest_url = ""
  else:
    parser = IndexHtmlParser()
    with open("build/index.html", "r") as input_file:
      parser.feed(input_file.read())
    script_urls = parser.script_urls
    manifest_url = parser.manifest_url

  return {
      "script_urls": script_urls,
      "manifest_url": manifest_url,
  }
