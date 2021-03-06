# coding=utf-8
#
#  Example 9 - Creating a payment for a customer
#
from __future__ import print_function

import os
import time

import flask

from app import database_write
from mollie.api.client import Client
from mollie.api.error import Error


def main():
    try:
        #
        # Initialize the Mollie API library with your API key.
        #
        # See: https://www.mollie.com/dashboard/settings/profiles
        #
        api_key = os.environ.get('MOLLIE_API_KEY', 'test_test')
        mollie_client = Client()
        mollie_client.set_api_key(api_key)

        body = ''

        customer_id = flask.request.args.get('customer_id')

        # If no customer ID was provided in the URL, we grab the first customer
        customer = None
        if customer_id is None:
            customers = mollie_client.customers.list()

            body += '<p>No customer ID specified. Attempting to retrieve the first page of '
            body += 'customers and grabbing the first.</p>'

            if not len(customers):
                body += '<p>You have no customers. You can create one from the examples.</p>'
                return body

            customer = next(customers)

        if not customer:
            customer = mollie_client.customers.get(customer_id)

        #
        # Generate a unique order number for this example. It is important to include this unique attribute
        # in the redirectUrl (below) so a proper return page can be shown to the customer.
        #
        order_id = int(time.time())

        #
        # See: https://www.mollie.com/nl/docs/reference/customers/create-payment
        #
        payment = mollie_client.customer_payments.with_parent_id(customer_id).create({
            'amount': {
                'currency': 'EUR',
                'value': '100.00'
            },
            'description': 'My first API payment',
            'webhookUrl': '{root}2-webhook_verification'.format(root=flask.request.url_root),
            'redirectUrl': '{root}3-return-page?order_id={id}'.format(root=flask.request.url_root, id=order_id),
            'metadata': {
                'order_id': order_id
            },
        })

        database_write(order_id, payment.status)

        return '<p>Created payment of {curr} {value} for {cust} ({id})<p>'.format(
            curr=payment.amount['currency'], value=payment.amount['value'], cust=customer.name, id=customer.id)

    except Error as err:
        return 'API call failed: {error}'.format(error=err)


if __name__ == '__main__':
    print(main())
