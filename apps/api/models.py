from django.db import models
from django.utils.translation import ugettext_lazy as _

API_KEY_MAX_LENGTH = 63
NAME_MAX_LENGTH = 63
DETAILS_MAX_LENGTH = 255
TOKEN_MAX_LENGTH = 31


class Subscriber(models.Model):
  # Name of subscriber.
  name = models.CharField(
      blank=False,
      max_length=NAME_MAX_LENGTH,
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
      max_length=API_KEY_MAX_LENGTH,
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
    Define a class of boxes in terms of its outcomes, their probabilities, and other parameters.
  """
  _pending_outcomes = None

  # User-defined name.
  name = models.CharField(
      blank=False,
      null=False,
      max_length=NAME_MAX_LENGTH,
      db_index=True,
      verbose_name=_("name"),
  )

  # User-defined details (whatever the user desires, typically descriptive text)
  details = models.CharField(
      blank=True,
      null=True,
      max_length=DETAILS_MAX_LENGTH,
      db_index=False,
      verbose_name=_("details"),
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

  # Access to this box definition depends on this association.
  subscribers = models.ManyToManyField(to=Subscriber, related_name="box_definitions")

  @property
  def size(self):
    return 2**self.log2size

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
        outcome.box_definition_id = self.id
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

  # User-defined outcome name.
  name = models.CharField(
      blank=False,
      null=False,
      max_length=NAME_MAX_LENGTH,
      db_index=True,
      verbose_name=_("name"),
  )

  # User-defined details (typically instructions for display of results).
  details = models.CharField(
      blank=True,
      null=True,
      max_length=DETAILS_MAX_LENGTH,
      db_index=False,
      verbose_name=_("details"),
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

  # For stable sort.
  order = models.PositiveIntegerField(
      blank=False,
      null=False,
      default=0,
      verbose_name=_("order"),
  )


class BoxProspectus(models.Model):

  # The BoxDefinition
  box_definition = models.ForeignKey(
      blank=False,
      null=False,
      to=BoxDefinition,
      db_index=True,
      on_delete=models.CASCADE,
      related_name="box_prospectus",
  )

  # The initial random seed.
  initial_random_seed = models.BigIntegerField(
      blank=False,
      null=False,
      default=0,
      verbose_name=_("initial random seed"),
  )

  # The actual hit rate.  (Fraction of outcomes with positive amounts)
  actual_hit_rate = models.FloatField(
      blank=False,
      null=False,
      verbose_name=_("actual hit rate"),
  )

  # The actual return (sum of all outcome output amounts).
  actual_return = models.IntegerField(
      blank=False,
      null=False,
      verbose_name=_("actual return"),
  )

  # The maximum amount out
  max_amount_out = models.IntegerField(
      blank=False,
      null=False,
      verbose_name=_("max amount out"),
  )


def uint32(x):
  return ((1 << 31) - x) if x < 0 else x


def int32(x):
  return (x - (1 << 32)) if x >= (1 << 31) else x


class Box(models.Model):

  # Who this box belongs to.
  subscriber = models.ForeignKey(
      blank=False,
      null=False,
      to=Subscriber,
      on_delete=models.CASCADE,
      related_name="boxes",
  )

  # The series token.  An opaque code that identifies a consistent grouping of boxes.
  series_token = models.CharField(
      blank=False,
      null=False,
      max_length=TOKEN_MAX_LENGTH,
      db_index=True,
      verbose_name=_("series token"),
  )

  # The BoxProspectus
  box_prospectus = models.ForeignKey(
      blank=False,
      null=False,
      to=BoxProspectus,
      db_index=True,
      on_delete=models.CASCADE,
      related_name="boxes",
  )

  # The current randomizer state, consisting of 4 32-bit integers.
  random_state_0 = models.IntegerField(
      blank=True,
      null=False,
      default=0,
      verbose_name=_("rng state 0"),
  )
  random_state_1 = models.IntegerField(
      blank=True,
      null=False,
      default=0,
      verbose_name=_("rng state 1"),
  )
  random_state_2 = models.IntegerField(
      blank=True,
      null=False,
      default=0,
      verbose_name=_("rng state 2"),
  )
  random_state_3 = models.IntegerField(
      blank=True,
      null=False,
      default=0,
      verbose_name=_("rng state 3"),
  )

  @property
  def random_state(self):
    """ Use this, not the individual fields, to get the random state. """
    return (
        uint32(self.random_state_0),
        uint32(self.random_state_1),
        uint32(self.random_state_2),
        uint32(self.random_state_3),
    )

  @random_state.setter
  def random_state(self, state):
    self.random_state_0 = int32(state[0])
    self.random_state_1 = int32(state[1])
    self.random_state_2 = int32(state[2])
    self.random_state_3 = int32(state[3])

  # The current card count.
  card_count = models.PositiveIntegerField(
      blank=False,
      null=False,
      default=0,
      verbose_name=_("current state"),
  )

  # Open or closed.
  is_closed = models.BooleanField(
      blank=True,
      null=False,
      default=False,
      verbose_name=_("is closed"),
  )


class Card(models.Model):

  # The parent Box
  box = models.ForeignKey(
      blank=False,
      null=False,
      to=Box,
      db_index=True,
      on_delete=models.CASCADE,
      related_name="cards",
  )

  # The outcome.
  outcome = models.ForeignKey(blank=True, null=True, to=Outcome, on_delete=models.CASCADE)

  # The sequence number.
  sequence = models.PositiveIntegerField(
      blank=False,
      null=False,
      db_index=True,
      verbose_name=_("sequence"),
  )

  # The assigned user token.
  user_token = models.CharField(
      blank=False,
      null=False,
      max_length=TOKEN_MAX_LENGTH,
      db_index=True,
      verbose_name=_("user token"),
  )

  # Whether this card has been consumed.
  consumed = models.BooleanField(
      blank=False,
      null=False,
      default=False,
      db_index=True,
      verbose_name=_("consumed"),
  )
