import logging

from .crud import change_locations

log = logging.getLogger(__name__)

def update_location():
    log.info('task worked')
    change_locations()