from random import shuffle
from web3.eth import Contract
from ..common.typing import List, DictOfAny
from ..common.const import VALIDATION_DEFAULTS
from ..common.utils import get_from_first
from ..common.logging import getLogger

log = getLogger(__name__)


def select_random_pin_for_validation(scatter: Contract, pins: List[DictOfAny], options: DictOfAny) -> int:
    """ Select a pin to validate at random, as long as the bid fits our criterea """
    total = len(pins)
    log.debug('Selecting from {} total pins.'.format(total))
    if total < 1:
        return -1

    min_file_size = get_from_first('min_file_size', options, VALIDATION_DEFAULTS)
    max_file_size = get_from_first('max_file_size', options, VALIDATION_DEFAULTS)
    min_reward = get_from_first('min_reward', options, VALIDATION_DEFAULTS)
    min_duration = get_from_first('min_duration', options, VALIDATION_DEFAULTS)
    max_duration = get_from_first('max_duration', options, VALIDATION_DEFAULTS)

    pin_idx_range = list(range(0, total))
    shuffle(pin_idx_range)

    for idx in pin_idx_range:
        log.debug('Checking pin #{}'.format(idx))
        pin = pins[idx]
        bid_id = pin.get('bid_id')

        if bid_id is None:
            raise ValueError("Provided pin missing bid_id")

        (
            bidder,
            file_hash,
            file_size,
            bid_value,
            validation_pool,
            duration,
            min_valid
        ) = scatter.functions.getBid(bid_id).call()
        validation_count = scatter.functions.getValidationCount(bid_id).call()

        # Only return something we want
        if (file_size < min_file_size
                or file_size > max_file_size
                or (validation_count != 0 and (validation_pool // validation_count) < min_reward)
                or duration < min_duration
                or duration > max_duration):
            log.debug('Pin #{} does not meet criteria.'.format(idx))
            continue
        else:
            log.debug('Selecting pin #{}.'.format(idx))
            return bid_id
    return -1
