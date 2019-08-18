from django.utils.deconstruct import deconstructible


@deconstructible
class UserUploadPath(object):
  """Return dynamic upload_to paths, containing user id, for file/image fields.

    Usage:
        `upload_to = UserUploadPath('photos/')`
        will store to MEDIA_ROOT/user-id-<user.id>/photos/<filename>

    Reference:
        - https://code.djangoproject.com/ticket/22999
    """
  path = "{0}/{1}/{2}"

  def __init__(self, sub_path):
    self.sub_path = sub_path

  def __call__(self, instance, filename):
    return self.path.format(instance.user.id, self.sub_path, filename)
