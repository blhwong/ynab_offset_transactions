import json
import datetime
import logging
from ynab import YNABClient


log = logging.getLogger()
log.setLevel(logging.INFO)

date_format = '%Y-%m-%d'
time_format = '%Y-%m-%d %H:%M:%S%Z'

brandon_budget_id = 'fdfb98f5-1b6d-4cde-ba34-2cb34b75cc1b'
shared_account_id = 'd63ceea2-11b5-4492-937f-697bee97942a'
now = datetime.datetime.now().strftime(time_format)

client = YNABClient('975ecaf89cf6de03f89c701b48f0e834117068d814e266a3e400cd5195fd6087')


def lambda_handler(event, context):
    log.info('event=%s context=%s', event, context)
    return offset_transactions(brandon_budget_id, shared_account_id, 'RY')


def offset_transactions(budget_id, account_id, payee_name):
    transaction_response = client.get_transactions(budget_id)
    transactions_to_offset = [t for t in transaction_response['data']['transactions'] if should_offset_transaction(t)]
    if not len(transactions_to_offset):
        log.info("No transactions to update.")
        return 0

    transactions_to_create = get_transactions_to_offset([t for t in transactions_to_offset], account_id, payee_name)
    transactions_to_complete = get_transactions_to_complete([t for t in transactions_to_offset])

    client.create_transactions(budget_id, transactions_to_create)
    client.update_transactions(budget_id, transactions_to_complete)
    log.info('%d transactions complete.', len(transactions_to_offset))
    return len(transactions_to_offset)


def should_offset_transaction(t):
    return (
        t['flag_color'] == 'yellow' and
        t['cleared'] == 'cleared' and
        t['approved']
    )


def create_transaction(account_id, date, amount, payee_name, category_id, memo):
    return {
        'account_id': account_id,
        'date': date,
        'amount': amount,
        'payee_name': payee_name,
        'category_id': category_id,
        'memo': memo,
    }


def get_transactions_to_offset(transactions_to_offset, account_id, payee_name):
    transactions = []
    for t in transactions_to_offset:
        memo = []
        transaction_payee_name = t['payee_name']
        if t['memo']:
            memo.append(t['memo'])
        memo.append(f'Added at {now} ({transaction_payee_name})')
        transaction = create_transaction(
            account_id,
            datetime.date.today().strftime(date_format),
            abs(t['amount']),
            payee_name,
            t['category_id'],
            ' | '.join(memo),
        )
        transactions.append(transaction)

    return transactions


def get_transactions_to_complete(transactions_to_complete):
    transactions = []
    for t in transactions_to_complete:
        t['flag_color'] = 'green'
        memo = []
        if t['memo']:
            memo.append(t['memo'])
        memo.append(f'Completed at {now}')
        t['memo'] = ' | '.join(memo)
        transactions.append(t)

    return transactions
