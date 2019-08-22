from django.db import models
from django.utils.translation import ugettext_lazy as _


class Subscriber(models.Model):
  # Name of subscriber.
  name = models.CharField(
      blank=False,
      max_length=63,
      null=False,
      db_index=True,
      unique=True,
      verbose_name=_("name"),
  )

  def __str__(self):
    return self.name


class ApiKey(models.Model):
  # Who this key belongs to.
  subscriber = models.ForeignKey(
      blank=False,
      null=False,
      to=Subscriber,
      on_delete=models.CASCADE,
      related_name="api_keys",
  )

  # API keys are random ASCII strings.
  api_key = models.CharField(
      blank=False,
      null=False,
      max_length=63,
      unique=True,
      verbose_name=_("API key"),
  )

  # API keys are deactivated but never deleted.
  deactivated = models.BooleanField(
      blank=False,
      default=False,
      null=False,
      verbose_name=_("deactivated"),
  )


class BoxDefinition(models.Model):
  """
    This is a template from which boxes may be generated.
  """
  _pending_outcomes = None

  # Who this box definition belongs to.
  subscriber = models.ForeignKey(
      blank=True,
      null=True,
      to=Subscriber,
      on_delete=models.CASCADE,
      related_name="box_definitions",
  )

  # User-defined title string.
  title = models.CharField(
      blank=False,
      null=False,
      max_length=63,
      db_index=True,
      verbose_name=_("title"),
  )

  # User-defined description.
  description = models.CharField(
      blank=True,
      null=True,
      max_length=255,
      db_index=False,
      verbose_name=_("description"),
  )

  # The log base 2 of the size of this box.
  log2size = models.PositiveIntegerField(
      blank=False,
      null=False,
      default=22,
      verbose_name=_("log2(size)"),
  )

  # The amount staked.
  amount_in = models.PositiveIntegerField(
      blank=False,
      null=False,
      default=1,
      verbose_name=_("amount in"),
  )

  @property
  def size(self):
    return 2**self.log2size

  @property
  def hit_rate(self):
    return sum(outcome.hit_rate for outcome in self.outcomes)

  @property
  def average_return(self):
    return sum(outcome.average_return for outcome in self.outcomes)

  def __setattr__(self, name, value):
    if name == "outcomes":
      for outcome in value:
        outcome.box_definition = self
      if self.pk:
        for outcome in value:
          outcome.save()
      else:
        self._pending_outcomes = value
    else:
      super().__setattr__(name, value)

  def __getattribute__(self, name):
    if name == "outcomes":
      if self.pk:
        return list(self.saved_outcomes.all())
      else:
        return self._pending_outcomes or []
    else:
      return super().__getattribute__(name)

  def save(self, *args, **kwargs):
    is_new = not self.pk
    super().save(*args, **kwargs)
    if is_new and self._pending_outcomes:
      for outcome in self._pending_outcomes:
        outcome.save()
      self._pending_outcomes = None


class Outcome(models.Model):
  # Reference the parent box definition.
  box_definition = models.ForeignKey(
      blank=False,
      null=False,
      to=BoxDefinition,
      on_delete=models.CASCADE,
      related_name="saved_outcomes",
  )

  # User-defined title string.
  title = models.CharField(
      blank=False,
      null=False,
      max_length=63,
      db_index=True,
      verbose_name=_("title"),
  )

  # User-defined description.
  description = models.CharField(
      blank=True,
      null=True,
      max_length=255,
      db_index=False,
      verbose_name=_("description"),
  )

  # Numerator of the probability of this outcome (the denominator is the box size).
  probability = models.PositiveIntegerField(
      blank=False,
      null=False,
      default=1,
      verbose_name=_("probability"),
  )

  # The amount returned.
  amount_out = models.PositiveIntegerField(
      blank=False,
      null=False,
      default=0,
      verbose_name=_("amount out"),
  )

  @property
  def hit_rate(self):
    return self.probability / self.box_definition.size

  @property
  def average_return(self):
    return self.hit_rate * self.amount_out / self.box_definition.amount_in
