import random

from api.models import (Box, BoxDefinition, Outcome)


class BoxGenerator(object):
  def __init__(self, box_definition):
    def _assemble_outcomes():
      outcomes = []
      total_probability = 0
      for outcome in box_definition.outcomes:
        total_probability += outcome.probability
        outcomes.append({
            "outcome": outcome,
            "probability": outcome.probability,
            "order": outcome.order,
        })
      if total_probability < box_definition.size:
        outcomes.append({
            "probability": box_definition.size - total_probability,
            "order": 0,
        })
      outcomes = sorted(outcomes, key=lambda o: (o["probability"], o["order"]), reverse=True)
      breakpoint = 0
      for outcome in outcomes:
        outcome["breakpoint"] = breakpoint
        breakpoint += outcome["probability"]
      return outcomes

    self.box_definition = box_definition
    self.outcomes = _assemble_outcomes()

  def generate(self):
    seed = int(random.getrandbits(32))
    random.seed(self.seed)

    total_amount_out = 0
    max_amount_out = 0
    hit_count = 0
    for i in range(0, self.box_definition.size):
      x = random.randInt(0, self.box_definition.size - 1)
      outcome = _find_outcome(x)
      if outcome and outcome.amount_out > 0:
        total_amount_out += outcome.amount_out
        max_amount_out = max(max_amount_out, outcome.amount_out)
        hit_count += 1
    return Box(
        definition=self.box_definition,
        seed=seed,
        actual_hit_rate=(hit_count / self.box_definition.size),
        actual_return=(
            total_amount_out / self.box_definition.amount_in / self.box_definition.size),
        max_amount_out=max_amount_out,
    )


class BoxDefinitionService(object):
  def __init__(self, box_definition):
    self.box_definition = box_definition

  @property
  def hit_rate(self):
    return sum(OutcomeService(outcome).hit_rate for outcome in self.box_definition.outcomes)

  @property
  def average_return(self):
    return sum(OutcomeService(outcome).average_return for outcome in self.box_definition.outcomes)

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
        seed=seed,
        actual_hit_rate=(hit_count / self.box_definition.size),
        actual_return=actual_return,
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


class OutcomeService(object):
  def __init__(self, outcome):
    self.outcome = outcome

  @property
  def hit_rate(self):
    return self.outcome.probability / self.outcome.box_definition.size

  @property
  def average_return(self):
    return self.outcome.hit_rate * self.outcome.amount_out / self.outcome.box_definition.amount_in
