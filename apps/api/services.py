import random

from api.models import (Box, BoxDefinition, BoxProspectus, Card)
from api.operations import BoxDefinitionOperations, CardClaimValidator


class ServiceManager(object):
  def __init__(self, **kwargs):
    self.kwargs = kwargs

  @property
  def subscriber(self):
    return self.kwargs.get("subscriber")

  @property
  def box_definition(self):
    return self.kwargs.get("box_definition")

  def create_box_definition(self, **kwargs):
    box_definition = BoxDefinitionOperations(**kwargs).build()
    box_definition.subscribers.add(self.subscriber)
    return box_definition

  def get_box_definitions(self):
    return self.subscriber.box_definitions.all()

  def validate_box_definition(self, **kwargs):
    return BoxDefinitionOperations(**kwargs).validate()

  def get_box_definition(self, pk):
    return self.subscriber.box_definitions.get(pk=pk)

  def claim_card(self, consume=False, **kwargs):
    user_token, series_token = CardClaimValidator(**kwargs).validate()
    return ClaimCardOperation(self, user_token, series_token).run(consume)


class ClaimCardOperation:
  def __init__(self, service, user_token, series_token):
    self.service = service
    self.user_token = user_token
    self.series_token = series_token

  @property
  def subscriber(self):
    return self.service.subscriber

  @property
  def box_definition(self):
    return self.service.box_definition

  def run(self, consume):
    card = self._get_or_create_card()
    if consume:
      card.consumed = True
    return card

  def _get_or_create_card(self):
    return self._get_existing_card() or self._create_new_card()

  def _get_existing_card(self):
    return Card.objects.filter(
        box__box_prospectus__box_definition=self.box_definition,
        box__subscriber=self.subscriber,
        box__series_token=self.series_token,
        user_token=self.user_token,
        consumed=False,
    ).first()

  def _create_new_card(self):
    # First, we need a box.
    box = self._get_or_create_box()
    return self._generate_next_card(box)

  def _get_or_create_box(self):
    return self._get_existing_box() or self._create_new_box()

  # TODO: locking, wait don't generate
  def _get_existing_box(self):
    return Box.objects.filter(
        box_prospectus__box_definition=self.box_definition,
        subscriber=self.subscriber,
        series_token=self.series_token,
        is_closed=False,
    ).first()

  def _create_new_box(self):
    box_prospectus = self._create_new_box_prospectus()
    box = Box(
        subscriber=self.subscriber,
        series_token=self.series_token,
        box_prospectus=box_prospectus,
        random_state=box_prospectus.initial_random_state)
    box.save()
    return box

  def _create_new_box_prospectus(self):
    seed = int(random.getrandbits(48))
    random.seed(seed)
    box_stats = BoxStats(self.box_definition)
    outcome_index = OutcomeIndex(self.box_definition)
    for i in range(0, self.box_definition.size):
      x = random.getrandbits(self.box_definition.log2size)
      outcome = outcome_index.rand_to_outcome(x)
      box_stats.accum(outcome)
    box_prospectus = BoxProspectus(
        box_definition=self.box_definition,
        initial_random_state=seed,
        actual_hit_rate=box_stats.actual_hit_rate,
        actual_return=box_stats.actual_return,
        max_amount_out=box_stats.max_amount_out,
    )
    box_prospectus.save()
    return box_prospectus

  # TODO: locking, locking, locking
  def _generate_next_card(self, box):
    outcome_index = OutcomeIndex(self.box_definition)
    random.seed(box.random_state)
    x = random.getrandbits(self.box_definition.log2size)
    outcome = outcome_index.rand_to_outcome(x)
    card = Card(
        box=box,
        outcome=outcome,
        sequence=box.card_count,
        user_token=self.user_token,
    )
    card.save()

    # TODO: really save state
    box.random_state = random.getstate()[0]
    box.card_count += 1
    if box.card_count >= self.box_definition.size:
      box.is_closed = True
    box.save()
    return card


class OutcomeIndex:
  def __init__(self, box_definition):
    self.box_definition = box_definition
    self.result_lookup = []
    total_probability = 0
    for outcome in self.box_definition.outcomes:
      total_probability += outcome.probability
      self.result_lookup.append({
          "outcome": outcome,
          "probability": outcome.probability,
          "order": outcome.order,
      })
    if total_probability < self.box_definition.size:
      self.result_lookup.append({
          "outcome": None,
          "probability": self.box_definition.size - total_probability,
          "order": 0,
      })
    self.result_lookup = sorted(
        self.result_lookup, key=lambda o: (o["probability"], o["order"]), reverse=True)
    breakpoint = 0
    for obj in self.result_lookup:
      breakpoint += obj["probability"]
      obj["breakpoint"] = breakpoint

  def rand_to_outcome(self, x):
    for obj in self.result_lookup:
      if x < obj["breakpoint"]:
        return obj["outcome"]
    raise ValueError(f"{x} exceeds final breakpoint {obj['breakpoint']}")


class BoxStats:
  def __init__(self, box_definition):
    self._box_definition = box_definition
    self._total_amount_out = 0
    self._max_amount_out = 0
    self._hit_count = 0

  def accum(self, outcome):
    if outcome and outcome.amount_out > 0:
      self._total_amount_out += outcome.amount_out
      self._max_amount_out = max(self._max_amount_out, outcome.amount_out)
      self._hit_count += 1

  @property
  def actual_return(self):
    return self._total_amount_out / (self._box_definition.size * self._box_definition.amount_in)

  @property
  def actual_hit_rate(self):
    return self._total_amount_out / (self._box_definition.size * self._box_definition.amount_in)

  @property
  def max_amount_out(self):
    return self._max_amount_out
