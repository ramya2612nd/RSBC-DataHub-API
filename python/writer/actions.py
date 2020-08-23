import logging
from python.common.message import encode_message
from python.writer.config import Config
import python.common.email as email
import json

logging.basicConfig(level=Config.LOG_LEVEL)


def has_hold_expired(**args):
    # TODO - complete this method
    logging.info('has hold expired - method not implemented')
    return True, args


def add_do_not_process_until_attribute(**args):
    # TODO - complete this method
    return True, args


def write_back_to_watch_queue(**args):
    logging.critical('write_back_to_watch_queue: method not implemented')
    # TODO - complete this method
    return True, args


def save_application_to_vips(**args):
    # TODO - complete this method
    return True, args


def unable_to_place_on_hold(**args):
    return args


def add_to_failed_write_queue_and_acknowledge(**args):
    config = args.get('config')
    message = args.get('message')
    writer = args.get('writer')
    channel = args.get('channel')
    method = args.get('method')
    logging.warning('writing to failed write queue')
    if writer.publish(config.FAIL_QUEUE, encode_message(message, config.ENCRYPT_KEY)):
        channel.basic_ack(delivery_tag=method.delivery_tag)
    else:
        logging.critical('unable to write to RabbitMQ {} queue'.format(config.FAIL_QUEUE))
    return args


def add_to_watch_queue_and_acknowledge(**args):
    config = args.get('config')
    message = args.get('message')
    writer = args.get('writer')
    channel = args.get('channel')
    method = args.get('method')
    logging.warning('writing back to watch queue')
    if writer.publish(config.WATCH_QUEUE, encode_message(message, config.ENCRYPT_KEY)):
        channel.basic_ack(delivery_tag=method.delivery_tag)
    else:
        logging.critical('unable to write to RabbitMQ {} queue'.format(config.WATCH_QUEUE))
    return args


def unable_to_send_email(**args):
    logging.critical('unable to send email')
    return args


def do_nothing(**args):
    logging.debug('do nothing')
    return args


def unable_to_acknowledge_receipt(**args):
    logging.critical('unable to acknowledge receipt to RabbitMQ')
    config = args.get('config')
    title = 'Critical Error: Unable to acknowledge receipt to RabbitMQ'
    body = 'Unable to acknowledge receipt to RabbitMQ'
    email.send_email_to_admin(config=config, title=title, body=body)
    return args


def unable_to_save_to_vips_api(**args):
    logging.critical('inside unable_to_save_to_vips_api()')
    config = args.get('config')
    message = args.get('message')
    title = 'Critical Error: Unable to save to VIPS'
    body_text = 'While attempting to save an application to VIPS, an error was returned. ' + \
                'We will save the record to a failed write queue in RabbitMQ.'
    logging.critical('unable to save to VIPS: {}'.format(json.dumps(message)))
    email.send_email_to_admin(config=config, title=title, body=body_text)
    return args


def unknown_event_type(**args) -> tuple:
    message = args.get('message')
    config = args.get('config')
    title = 'Critical Error: Unknown Event Type'
    body_text = "An unknown event has been received: " + message['event_type']
    logging.critical('unknown event type: {}'.format(message['event_type']))
    email.send_email_to_admin(config=config, title=title, body=body_text)
    # Note deliberately returns True because this is a "success"
    # function with no associated failure function.
    return True, args

