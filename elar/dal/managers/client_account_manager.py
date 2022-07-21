# -*- coding: utf-8 -*-
from elar.models import ClientAccount, ClientAccountUser
from elar import db


class ClientAccountManager:
    @staticmethod
    def get_client_accounts_by_user_id(user_id):
        return (
            ClientAccount.query.join(
                ClientAccountUser,
                ClientAccount.id == ClientAccountUser.client_account_id,
            )
            .filter(ClientAccountUser.user_id == user_id)
            .filter(ClientAccountUser.is_active.is_(True))
            .all()
        )

    @staticmethod
    def get_accounting_currency_code(client_account_id):
        return (
            db.session.query(ClientAccount.accounting_currency)
            .filter(ClientAccount.id == client_account_id)
            .scalar()
        )

    @staticmethod
    def get_next_sequence_number(client_account_id):
        seq = 1
        client_account = (
            db.session.query(ClientAccount)
            .with_for_update()
            .filter(ClientAccount.id == client_account_id)
            .first()
        )
        if not client_account.sequence_number:
            client_account.sequence_number = seq
        else:
            client_account.sequence_number = client_account.sequence_number + 1
            seq = client_account.sequence_number
        db.session.add(client_account)
        return seq

    @staticmethod
    def get_next_recon_sequence_number(client_account_id):
        seq = 1
        client_account = (
            db.session.query(ClientAccount)
            .with_for_update()
            .filter(ClientAccount.id == client_account_id)
            .first()
        )
        if not client_account.recon_seq_num:
            client_account.recon_seq_num = seq
        else:
            client_account.recon_seq_num += 1
            seq = client_account.recon_seq_num
        db.session.add(client_account)
        return seq


    @staticmethod
    def get_next_sale_invoice_sequence_number(client_account_id):
        seq = 10000
        client_account = (
            db.session.query(ClientAccount)
            .with_for_update()
            .filter(ClientAccount.id == client_account_id)
            .first()
        )
        if not client_account.sale_invoice_seq_number:
            client_account.sale_invoice_seq_number = seq
        else:
            client_account.sale_invoice_seq_number += 1
            seq = client_account.sale_invoice_seq_number
        db.session.add(client_account)
        return seq

    @staticmethod
    def get_next_purchase_invoice_sequence_number(client_account_id):
        seq = 20000
        client_account = (
            db.session.query(ClientAccount)
            .with_for_update()
            .filter(ClientAccount.id == client_account_id)
            .first()
        )
        if not client_account.purchase_invoice_seq_number:
            client_account.purchase_invoice_seq_number = seq
        else:
            client_account.purchase_invoice_seq_number += 1
            seq = client_account.purchase_invoice_seq_number
        db.session.add(client_account)
        return seq

    @staticmethod
    def get_next_sale_credit_notes_sequence_number(client_account_id):
        seq = 10000
        client_account = (
            db.session.query(ClientAccount)
            .with_for_update()
            .filter(ClientAccount.id == client_account_id)
            .first()
        )
        if not client_account.sale_credit_notes_seq_number:
            client_account.sale_credit_notes_seq_number = seq
        else:
            client_account.sale_credit_notes_seq_number += 1
            seq = client_account.sale_credit_notes_seq_number
        db.session.add(client_account)
        return seq

    @staticmethod
    def get_next_purchase_credit_notes_sequence_number(client_account_id):
        seq = 20000
        client_account = (
            db.session.query(ClientAccount)
            .with_for_update()
            .filter(ClientAccount.id == client_account_id)
            .first()
        )
        if not client_account.purchase_credit_notes_seq_number:
            client_account.purchase_credit_notes_seq_number = seq
        else:
            client_account.purchase_credit_notes_seq_number += 1
            seq = client_account.purchase_credit_notes_seq_number
        db.session.add(client_account)
        return seq

    @staticmethod
    def get_next_receipt_sequence_number(client_account_id):
        seq = 10000
        client_account = (
            db.session.query(ClientAccount)
            .with_for_update()
            .filter(ClientAccount.id == client_account_id)
            .first()
        )
        if not client_account.receipt_seq_number:
            client_account.receipt_seq_number = seq
        else:
            client_account.receipt_seq_number += 1
            seq = client_account.receipt_seq_number
        db.session.add(client_account)
        return seq

    @staticmethod
    def get_next_payment_sequence_number(client_account_id):
        seq = 20000
        client_account = (
            db.session.query(ClientAccount)
            .with_for_update()
            .filter(ClientAccount.id == client_account_id)
            .first()
        )
        if not client_account.payment_seq_number:
            client_account.payment_seq_number = seq
        else:
            client_account.payment_seq_number += 1
            seq = client_account.payment_seq_number
        db.session.add(client_account)
        return seq
