"""Offset transactions lambda"""
import os
import datetime
import logging
from ynab import YNABClient


log = logging.getLogger()
log.setLevel(logging.INFO)

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S%Z'

access_token = os.environ.get('YNAB_ACCESS_TOKEN')
now = datetime.datetime.now().strftime(TIME_FORMAT)

client = YNABClient(access_token)


def lambda_handler(event, context):
    """Lambda event handler"""
    log.info('event=%s context=%s', event, context)
    return offset_transactions(
        event['budget_id'],
        event['account_id'],
        event['offset_payee_name'],
        event['owner_payee_name'],
    )


def offset_transactions(budget_id, account_id, payee_name, owner_payee_name):
    """Offset Transactions handler"""
    transaction_response = client.get_transactions(budget_id)
    transactions_to_offset = [
        t for t in transaction_response['data']['transactions'] if should_offset_transaction(t)
    ]
    if not transactions_to_offset:
        log.info("No transactions to update.")
        return 0

    transactions_to_create = get_transactions_to_offset(
        list(transactions_to_offset),
        account_id,
        payee_name,
        owner_payee_name,
    )
    transactions_to_complete = get_transactions_to_complete(list(transactions_to_offset))

    client.create_transactions(budget_id, transactions_to_create)
    client.update_transactions(budget_id, transactions_to_complete)
    log.info('%d transactions complete.', len(transactions_to_offset))
    return len(transactions_to_offset)


def should_offset_transaction(transaction):
    """Determines whether transactions should be offset"""
    return (
        transaction['flag_color'] == 'yellow' and
        transaction['cleared'] == 'cleared' and
        transaction['approved']
    )


def create_transaction(account_id, date, amount, payee_name, category_id, memo):
    """Creates transaction object"""
    return {
        'account_id': account_id,
        'date': date,
        'amount': amount,
        'payee_name': payee_name,
        'category_id': category_id,
        'memo': memo,
    }


def get_transactions_to_offset(transactions_to_offset, account_id, payee_name, owner_payee_name):
    """Gets list of transactions to offset"""
    transactions = []
    for transaction in transactions_to_offset:
        memo = []
        transaction_payee_name = transaction['payee_name']
        if transaction['memo']:
            memo.append(transaction['memo'])
        memo.append(f'Added at {now} ({transaction_payee_name})')
        amount = transaction['amount']
        transaction = create_transaction(
            account_id,
            datetime.date.today().strftime(DATE_FORMAT),
            -amount,
            get_payee_name(amount, payee_name, owner_payee_name),
            transaction['category_id'],
            ' | '.join(memo),
        )
        transactions.append(transaction)

    return transactions


def get_transactions_to_complete(transactions_to_complete):
    """Gets transactions to complete"""
    transactions = []
    for transaction in transactions_to_complete:
        transaction['flag_color'] = 'green'
        memo = []
        if transaction['memo']:
            memo.append(transaction['memo'])
        memo.append(f'Completed at {now}')
        transaction['memo'] = ' | '.join(memo)
        transactions.append(transaction)

    return transactions

def get_payee_name(amount, payee_name, owner_payee_name):
    """
        Gets payee name.
        Uses owner payee name if amount > 0
        Example: Owner owes shared account because owner received a refund etc.
    """
    return payee_name if amount < 0 else owner_payee_name
