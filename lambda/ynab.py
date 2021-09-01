import json
import requests
import logging


log = logging.getLogger()
log.setLevel(logging.INFO)


class YNABClient:
    def __init__(self, token):
        self.base_url = 'https://api.youneedabudget.com/v1'
        self.headers = { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json' }


    def get_budgets(self):
        path = f'/budgets'
        try:
            res = requests.get(self.base_url + path, headers=self.headers)
            return res.json()
        except Exception as e:
            log.error('get_budgets error. %s', e)
            raise e


    def get_transactions(self, budget_id, since_date=None):
        path = f'/budgets/{budget_id}/transactions'
        params = { 'since_date': since_date }
        try:
            res = requests.get(self.base_url + path, params=params, headers=self.headers)
            return res.json()
        except Exception as e:
            log.error('get_transactions error. %s', e)
            raise e


    def update_transactions(self, budget_id, transactions):
        data = json.dumps({ 'transactions': transactions })
        path = f'/budgets/{budget_id}/transactions'
        try:
            res = requests.patch(self.base_url + path, data=data, headers=self.headers)
            return res.json()
        except Exception as e:
            log.error('update_transactions error. %s', e)
            raise e


    def create_transactions(self, budget_id, transactions):
        data = json.dumps({ 'transactions': transactions })
        path = f'/budgets/{budget_id}/transactions'
        try:
            res = requests.post(self.base_url + path, data=data, headers=self.headers)
            return res.json()
        except Exception as e:
            log.error('create_transactions error. %s', e)
            raise e


    def get_accounts(self, budget_id):
        path = f'/budgets/{budget_id}/accounts'
        try:
            res = requests.get(self.base_url + path, headers=self.headers)
            return res.json()
        except Exception as e:
            log.error('get_transactions error. %s', e)
            raise e
