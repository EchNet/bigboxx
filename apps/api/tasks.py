import os
from celery import shared_task
from datetime import timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task
def run_prepare_box_service(box_definition_id):
  logger.info(f"run_prepare_box_service({box_definition_id}): START")
  logger.info(f"run_prepare_box_service({box_definition_id}): END")
