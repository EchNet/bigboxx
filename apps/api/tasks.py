import os
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
import logging

from api.models import BoxDefinition, Box
from api.services import BoxDefinitionService

logger = logging.getLogger(__name__)


@shared_task
def run_prepare_box_service(box_definition_id):
  logger.info(f"run_prepare_box_service({box_definition_id}): START")

  try:
    box_definition = BoxDefinition.objects.get(box_definition_id)
    prepare_box_service(box_definition)
  except BoxDefinition.DoesNotExist:
    logger.error(f"No such box definition: {box_definition_id}")

  logger.info(f"run_prepare_box_service({box_definition_id}): END")


AMPLE_FREE_BOXES = 2
MAX_TRIALS = 12


def prepare_box_service(box_definition):
  logger.info(f"prepare box service {box_definition}")
  service = BoxDefinitionService(box_definition)
  trials = 0
  while trials < MAX_TRIALS and service.free_box_count() < AMPLE_FREE_BOXES:
    logger.info("Generating trial box...")
    t0 = timezone.now()
    box = service.generate_trial_box()
    t1 = timezone.now()
    logger.info("Generated trial box in {t1 - t0}...")
    if not service.box_is_acceptable(box):
      logger.info("Box not accepted: {box.stats}")
    else:
      logger.info("Box accepted: {box.stats}")
      t0 = timezone.now()
      service.commit_box(box)
      t1 = timezone.now()
      logger.info("Committed box in {t1 - t0}...")
  if trials == MAX_TRIALS:
    logger.error("GAVE UP")
