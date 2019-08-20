import dateutil

from django.core.validators import ValidationError
from django.utils import timezone


class FieldValidator:
  """
    A field validation utility, subordinate to ItemValidator.
  """

  def __init__(self, item_validator, field_name, dflt):
    self.item_validator = item_validator
    self.field_name = field_name
    self.value = item_validator.input_fields.get(field_name, dflt)

  def add_error(self, msg):
    if not self.item_validator.errors.get(self.field_name, None):
      self.item_validator.errors[self.field_name] = []
    self.item_validator.errors[self.field_name].append(msg)
    return _DisabledFieldValidator()  # No further validation in this chain.

  def keep(self, arg_name=None):
    if not arg_name:
      arg_name = self.field_name
    self.item_validator.valid_fields[arg_name] = self.value
    return self.value

  def to_be_truthy(self):
    if not self.value:
      return self.add_error("required")
    return self

  def to_be_string(self):
    try:
      self.value = str(self.value)
    except:
      return self.add_error("must be string")
    return self

  def to_be_integer(self):
    try:
      self.value = int(self.value)
    except:
      return self.add_error("must be integer")
    return self

  def to_be_positive_integer(self):
    try:
      self.value = int(self.value)
      if self.value <= 0:
        raise ValidationError()
    except:
      return self.add_error("must be positive integer")
    return self

  def to_be_array_of(self, element_builder):
    try:
      enumerator = enumerate(self.value)
    except:
      return self.add_error(f"must be array")

    new_values = []
    for ix, ele in enumerator:
      try:
        new_values.append(element_builder(ele))
      except ValidationError as ve:
        return self.add_error(f"element {ix}: {ve}")
    self.value = new_values
    return self

  def to_be_date(self):
    try:
      if isinstance(self.value, str):
        self.value = dateutil.parser.parse(self.value).date()
      # Raise an exception if value is incompatible with Date:
      if self.value > timezone.now().date():
        pass
    except:
      return self.add_error("must be date")
    return self

  def to_be_one_of(self, Enumeration):
    if not self.value in [ele[0] for ele in Enumeration.CHOICES]:
      return self.add_error("value out of range")
    return self

  def in_range(self, min, max):
    if self.value < min or self.value > max:
      return self.add_error("value out of range")
    return self

  def length_in_range(self, min, max):
    if len(self.value) < min or len(self.value) > max:
      return self.add_error("length out of range")
    return self


# This class substitutes for a FieldValidator when a method in the chain adds an error.
# Successive calls in the chain do nothing.
class _DisabledFieldValidator:
  def __getattr__(self, attr):
    def func(*args):
      return self

    return func


class ItemValidator:
  """
    A validation utility.
  """
  _field_validator_class = FieldValidator

  def __init__(self, input_fields):
    self.input_fields = input_fields
    self.recognized_field_names = []
    self.valid_fields = {}
    self.errors = {}

  def run(self):
    self._run_validation()
    self._check_extra_fields()
    self._check_errors()
    return self

  def _expect(self, field_name, dflt=None):
    self.recognized_field_names.append(field_name)
    return self._field_validator_class(self, field_name, dflt)

  def _allow(self, field_name):
    if self.input_fields.get(field_name, None) is not None:
      return self._expect(field_name, None)
    else:
      return _DisabledFieldValidator()

  def _check_extra_fields(self):
    fields = {**self.input_fields}
    for f in self.recognized_field_names:
      fields.pop(f, None)
    for f in fields.keys():
      self.errors[f] = ["unrecognized field"]

  def _check_errors(self):
    if self.errors:
      raise ValidationError(self.errors)

  # Must be subclassed.
  def _run_validation(self):
    raise ValueError("must be subclassed")
