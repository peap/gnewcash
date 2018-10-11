import gzip
import os.path
from datetime import datetime
from logging import getLogger
from xml.etree import ElementTree

from gnewcash.transaction import Split, Transaction, TransactionManager
from gnewcash.account import Account, AccountType


class GnuCashFile:
    namespace_data = {
        'gnc': 'http://www.gnucash.org/XML/gnc',
        'act': 'http://www.gnucash.org/XML/act',
        'book': 'http://www.gnucash.org/XML/book',
        'cd': 'http://www.gnucash.org/XML/cd',
        'cmdty': 'http://www.gnucash.org/XML/cmdty',
        'price': 'http://www.gnucash.org/XML/price',
        'slot': 'http://www.gnucash.org/XML/slot',
        'split': 'http://www.gnucash.org/XML/split',
        'sx': 'http://www.gnucash.org/XML/sx',
        'trn': 'http://www.gnucash.org/XML/trn',
        'ts': 'http://www.gnucash.org/XML/ts',
        'fs': 'http://www.gnucash.org/XML/fs',
        'bgt': 'http://www.gnucash.org/XML/bgt',
        'recurrence': 'http://www.gnucash.org/XML/recurrence',
        'lot': 'http://www.gnucash.org/XML/lot',
        'addr': 'http://www.gnucash.org/XML/addr',
        'owner': 'http://www.gnucash.org/XML/owner',
        'billterm': 'http://www.gnucash.org/XML/billterm',
        'bt-days': 'http://www.gnucash.org/XML/bt-days',
        'bt-prox': 'http://www.gnucash.org/XML/bt-prox',
        'cust': 'http://www.gnucash.org/XML/cust',
        'employee': 'http://www.gnucash.org/XML/employee',
        'entry': 'http://www.gnucash.org/XML/entry',
        'invoice': 'http://www.gnucash.org/XML/invoice',
        'job': 'http://www.gnucash.org/XML/job',
        'order': 'http://www.gnucash.org/XML/order',
        'taxtable': 'http://www.gnucash.org/XML/taxtable',
        'tte': 'http://www.gnucash.org/XML/tte',
        'vendor': 'http://www.gnucash.org/XML/vendor'
    }

    def __init__(self, books=None):
        if not books:
            books = []
        self.books = books
        self.file_name = None

    def __str__(self):
        as_string = ''
        if self.file_name:
            as_string = self.file_name + ', '
        as_string += '{} books'.format(len(self.books))
        return as_string

    def __repr__(self):
        return str(self)

    @classmethod
    def read_file(cls, source_file):
        logger = getLogger()
        built_file = GnuCashFile(None)
        built_file.file_name = source_file
        if os.path.exists(source_file):
            try:
                xml_tree = ElementTree.parse(source=source_file)
                root = xml_tree.getroot()
            except ElementTree.ParseError:
                with gzip.open(source_file, 'rb') as gzipped_file:
                    contents = gzipped_file.read().decode('utf-8')
                xml_tree = ElementTree.fromstring(contents)
                root = xml_tree
            namespaces = cls.namespace_data

            books = root.findall('gnc:book', namespaces)
            for book in books:
                new_book = Book()
                accounts = book.findall('gnc:account', namespaces)
                transactions = book.findall('gnc:transaction', namespaces)

                commodity = book.find('gnc:commodity', namespaces)
                new_book.commodity = Commodity(commodity.find('cmdty:id').text,
                                               commodity.find('cmty:space').text)

                account_objects = list()
                transaction_manager = TransactionManager()

                for account in accounts:
                    # Bring in the XML data
                    name = account.find('act:name', namespaces).text
                    account_id = account.find('act:id', namespaces).text
                    account_type = account.find('act:type', namespaces).text

                    parent = account.find('act:parent', namespaces)
                    if parent is not None:
                        parent = parent.text

                    account_object = Account()
                    account_object.guid = account_id
                    account_object.name = name
                    account_object.type = account_type

                    commodity = account.find('act:commodity', namespaces)
                    account_object.commodity = Commodity(commodity.find('cmdty:id').text,
                                                         commodity.find('cmdty:space').text)

                    if parent is not None:
                        parent_account = [x for x in account_objects if x.guid == parent]
                        if parent:
                            account_object.parent = parent_account[0]
                    else:
                        new_book.root_account = account_object
                    account_objects.append(account_object)

                for transaction in transactions:
                    date_entered = transaction.find('trn:date-entered', namespaces).find('ts:date', namespaces).text
                    date_posted = transaction.find('trn:date-posted', namespaces).find('ts:date', namespaces).text
                    description = transaction.find('trn:description', namespaces).text
                    splits = transaction.find('trn:splits', namespaces)
                    from_account = None
                    to_account = None
                    amount = None
                    from_account_reconciled = 'n'
                    to_account_reconciled = 'n'
                    memo = transaction.find('trn:num', namespaces)
                    if memo is not None:
                        memo = memo.text

                    date_entered = datetime.strptime(date_entered, '%Y-%m-%d %H:%M:%S %z')
                    date_posted = datetime.strptime(date_posted, '%Y-%m-%d %H:%M:%S %z')

                    for split in list(splits):
                        value = split.find('split:value', namespaces).text
                        account = split.find('split:account', namespaces).text
                        reconciled = split.find('split:reconciled-state', namespaces).text

                        account = [x for x in account_objects if x.guid == account][0]
                        value = float(value[:value.find('/')]) / 100

                        if amount is None:
                            amount = abs(value)

                        if value < 0:
                            from_account = account
                            from_account_reconciled = reconciled
                        elif value > 0:
                            to_account = account
                            to_account_reconciled = reconciled
                        else:
                            from_account = account
                            to_account = account

                    transaction = Transaction()
                    transaction.date_entered = date_entered
                    transaction.date_posted = date_posted
                    transaction.description = description
                    transaction.amount = amount
                    transaction.from_account = from_account
                    transaction.to_account = to_account
                    transaction.splits.append(Split(from_account, abs(amount) * -1, from_account_reconciled))
                    transaction.splits.append(Split(to_account, abs(amount), to_account_reconciled))
                    transaction.memo = memo

                    transaction_manager.add(transaction)

                new_book.transactions = transaction_manager
                built_file.books.append(new_book)
        else:
            logger.warning('Could not find %s', source_file)
        return built_file

    def build_file(self, target_file):
        namespace_info = self.namespace_data
        root_node = ElementTree.Element('gnc-v2', {'xmlns:' + identifier: value
                                                   for identifier, value in namespace_info.items()})
        for book in self.books:
            root_node.append(book.as_xml)

        element_tree = ElementTree.ElementTree(root_node)
        element_tree.write(target_file, encoding='utf-8', xml_declaration=True)


class Book:
    def __init__(self, root_account=None, transactions=None, commodity=None):
        self.root_account = root_account
        self.transactions = transactions or TransactionManager()
        self.commodity = commodity

    @property
    def as_xml(self):
        book_node = ElementTree.Element('gnc:book', {'version': '2.0.0'})
        book_node.append(self.commodity.as_xml)

        for account in self.root_account.as_xml:
            book_node.append(account)

        for transaction in self.transactions:
            book_node.append(transaction.as_xml)

        return book_node

    def get_account(self, *paths_to_account, current_level=None):
        if current_level is None:
            current_level = self.root_account
        paths_to_account = list(paths_to_account)
        next_level = paths_to_account.pop(0)
        for account in current_level.children:
            if account.name == next_level:
                if not paths_to_account:
                    return account
                return self.get_account(*paths_to_account, current_level=account)
        return None

    def get_account_balance(self, account):
        account_balance = 0
        account_transactions = [x for x in self.transactions if account in [x.from_account, x.to_account]]
        for transaction in account_transactions:
            if account.type == AccountType.CREDIT:
                transaction.amount *= -1
            if transaction.from_account == account:
                account_balance -= transaction.amount
            elif transaction.to_account == account:
                account_balance += transaction.amount
        return account_balance


class Commodity:
    def __init__(self, commodity_id, space):
        self.id = commodity_id
        self.space = space

    @property
    def as_xml(self):
        commodity_node = ElementTree.Element('gnc:commodity', {'version': '2.0.0'})
        ElementTree.SubElement(commodity_node, 'cmdty:space').text = self.space
        ElementTree.SubElement(commodity_node, 'cmdty:id').text = self.id
        ElementTree.SubElement(commodity_node, 'cmdty:getquotes')
        ElementTree.SubElement(commodity_node, 'cmdty:quote_source').text = 'currency'
        ElementTree.SubElement(commodity_node, 'cmdty:quote_tz')
        return commodity_node

    def as_short_xml(self, node_tag):
        commodity_node = ElementTree.Element(node_tag)
        ElementTree.SubElement(commodity_node, 'cmdty:space').text = self.space
        ElementTree.SubElement(commodity_node, 'cmdty:id').text = self.id
        return commodity_node
