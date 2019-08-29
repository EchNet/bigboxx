import random

from api.models import (Box, BoxDefinition, Card, Outcome)


class BoxDefinitionService(object):
  _result_lookup = None

  def __init__(self, box_definition):
    self.box_definition = box_definition

  @property
  def outcomes(self):
    return (OutcomeService(outcome) for outcome in self.box_definition.outcomes)

  @property
  def hit_rate(self):
    return sum(outcome.hit_rate for outcome in self.outcomes)

  @property
  def average_return(self):
    return sum(outcome.average_return for outcome in self.outcomes)

  @property
  def in_service(self):
    return self.free_box_count() > 0

  def free_box_count(self):
    return self.box_definition.boxes.count()

  def create_random_box(self):
    seed = int(random.getrandbits(32))
    random.seed(seed)
    max_amount_out = 0
    actual_return = 0
    hit_count = 0
    for i in range(0, self.box_definition.size):
      pass
    return Box(
        definition=self.box_definition,
        initial_seed=seed,
        actual_hit_rate=(hit_count / self.box_definition.size),
        actual_return=actual_return,
        max_amount_out=max_amount_out,
    )

  def _get_result_lookup(self):
    if self._result_lookup is None:
      self._result_lookup = self._assemble_result_lookup()
    return self._result_lookup

  def _assemble_result_lookup(self):
    result_lookup = []
    total_probability = 0
    for outcome in self.box_definition.outcomes:
      total_probability += outcome.probability
      result_lookup.append({
          "outcome": outcome,
          "probability": outcome.probability,
          "order": outcome.order,
      })
    if total_probability < self.box_definition.size:
      result_lookup.append({
          "outcome": None,
          "probability": self.box_definition.size - total_probability,
          "order": 0,
      })
    result_lookup = sorted(
        result_lookup, key=lambda o: (o["probability"], o["order"]), reverse=True)
    breakpoint = 0
    for obj in result_lookup:
      breakpoint += obj["probability"]
      obj["breakpoint"] = breakpoint
    return result_lookup

  def _rand_to_outcome(self, x):
    for obj in self._get_result_lookup():
      if x < obj["breakpoint"]:
        return obj["outcome"]
    raise ValueError(f"{x} exceeds final breakpoint {obj['breakpoint']}")

  def generate_box(self):
    seed = int(random.getrandbits(32))
    random.seed(seed)

    total_amount_out = 0
    max_amount_out = 0
    hit_count = 0
    for i in range(0, self.box_definition.size):
      x = random.randint(0, self.box_definition.size - 1)
      outcome = self._rand_to_outcome(outcomes)
      if outcome and outcome.amount_out > 0:
        total_amount_out += outcome.amount_out
        max_amount_out = max(max_amount_out, outcome.amount_out)
        hit_count += 1
    return Box(
        definition=self.box_definition,
        initial_seed=seed,
        actual_hit_rate=(hit_count / self.box_definition.size),
        actual_return=(
            total_amount_out / self.box_definition.amount_in / self.box_definition.size),
        max_amount_out=max_amount_out,
    )

  def box_is_acceptable(self, box):
    return True

  def claim_card(self, user_token):
    card = Card.objects.filter(
        box__box_definition=self.box_definition,
        user_token__isnull=True).select_for_update().get()
    card.user_token = user_token
    card.save()
    return card

  def generate_card(self, user_token):
    # TODO continue the sequence, deplete box
    x = random.randint(0, self.box_definition.size - 1)
    outcome = self._rand_to_outcome(x)
    card = Card(
        box=self.box_definition.boxes.all()[0],
        outcome=outcome,
        sequence=1,
        user_token=user_token,
    )
    card.save()
    return card


class OutcomeService(object):
  def __init__(self, outcome):
    self.outcome = outcome

  @property
  def hit_rate(self):
    return self.outcome.probability / self.outcome.box_definition.size

  @property
  def average_return(self):
    return self.hit_rate * self.outcome.amount_out / self.outcome.box_definition.amount_in
