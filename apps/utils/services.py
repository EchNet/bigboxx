#
# utils/services.py
# Support for application services.
#


class ServiceAggregator:
  class ContextElement:
    """
      A ContextElement describes the semantics of an entry in the context dictionary.
      This class must be subclassed for each element of the service context. 
    """

    class Meta:
      """
        At the minimum, every ContextElement subtype must have an inner Meta class 
        that defines KEY and TYPE. 
      """
      KEY = ""  # The property name, a string (e.g. "user").
      TYPE = object  # The property class.  A ValueError is raised if a value is incompatible.

    @classmethod
    def register(myclass, registry):
      """ Implementation method. """
      registry[myclass.Meta.KEY] = myclass()

    def get_implicit_elements(self, obj):
      """
        A ContextElement may identify additional associated values to be inserted
        into the context whenever this type of element is inserted.  For example, a
        User implies its Company.  Return a dictionary of element key to property
        value.  In the case of a User implying its company, this would be
        dict(company=obj.company).

        If a conflicting element already exists in the context, a ValueError is 
        raised.
      """
      return None

    def get_default_elements(self, obj):
      """
        A ContextElement may provide default values for other elements.  For example,
        a User might provide a default time zone.  Default values cannot conflict 
        with each other.  Return a dictionary of element key to property value, as
        get_implicit_elements does.
      """
      return None

  class _Context:
    """
      Implementation class, responsible for validating and maintaining context values.
    """

    def __init__(self, element_registry, values=None, defaults=None):
      self.element_registry = element_registry
      self.values = values or dict()
      self.defaults = defaults or dict()

    def assimilate(self, as_default=False, **kwargs):
      for key, value in kwargs.items():
        element = self.element_registry.get(key, None)
        if not element:
          raise ValueError(f"Unrecognized context element {key}.")
        if value is not None and not isinstance(value, element.Meta.TYPE):
          raise ValueError(f"{value} is not of type {element.Meta.TYPE}")
        if as_default:
          self.defaults[key] = value
        else:
          self.apply_element(element, key, value)
      return self

    def apply_element(self, element, key, value):
      if key in self.values:
        if self.values.get(key) != value:
          raise ValueError(f"Conflicting {key} values: {value} vs {self.values[key]}.")
      else:
        self.values[key] = value
        if value:
          implicit_elements = element.get_implicit_elements(value)
          if implicit_elements:
            self.assimilate(**implicit_elements)
          # Apply defaults after implicits, so that defaults set by implicits are overwritten
          # by our defaults.
          default_elements = element.get_default_elements(value)
          if default_elements:
            self.assimilate(True, **default_elements)

    def get(self, key):
      try:
        return (self.values if key in self.values else self.defaults).get(key)
      except KeyError:
        raise AttributeError(f"There is no {key} in context.")

    def clone(self):
      return self.__class__(self.element_registry, dict(**self.values), dict(**self.defaults))

  # Back to ServiceAggregator...

  _context_registry = None

  def __init__(self, context=None, **kwargs):
    """
      Construct a ServiceAggregator from context elements specified in kwargs.
    """
    self._context = (context or self._Context(self.get_context_registry())).assimilate(**kwargs)

  def add_context(self, **kwargs):
    """
      Add elements specified in kwargs to the context.
    """
    self._context.assimilate(**kwargs)

  def drill_down(self, **kwargs):
    """
      Create a new ServiceAggregator of the same type with additional context elements
      specified in kwargs.
    """
    return self.__class__(self._context.clone(), **kwargs)

  def __getattr__(self, key):
    """
      Expose context elements as read-only properties of the ServiceAggregator itself.
    """
    if key in self.get_context_registry():
      return self._context.get(key)
    raise AttributeError(key)

  @classmethod
  def get_context_registry(myclass):
    """ Implementation method. """
    if not myclass._context_registry:
      myclass._context_registry = {}
      for element_class in myclass.get_context_element_classes():
        element_class.register(myclass._context_registry)
    return myclass._context_registry
