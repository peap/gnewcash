# Stubs for gnewcash.account (Python 3)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

import abc
from collections import namedtuple
from datetime import datetime
from decimal import Decimal
from gnewcash.commodity import Commodity
from gnewcash.guid_object import GuidObject
from gnewcash.slot import SlottableObject
from typing import Any, Dict, List, Optional, Tuple, Union

LoanStatus = namedtuple('LoanStatus', ['iterator_balance', 'iterator_date', 'interest', 'amount_to_capital'])

LoanExtraPayment = namedtuple('LoanExtraPayment', ['payment_date', 'payment_amount'])

class Account(GuidObject, SlottableObject):
    name: str = ...
    type: Any = ...
    commodity_scu: Any = ...
    children: Any = ...
    commodity: Any = ...
    code: Any = ...
    description: Any = ...
    non_std_scu: Any = ...
    def __init__(self) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def as_dict(self, account_hierarchy: Dict[str, Account]=..., path_to_self: str=...) -> Dict[str, Account]: ...
    @property
    def dict_entry_name(self) -> str: ...
    def get_parent_commodity(self) -> Optional[Commodity]: ...
    def get_subaccount_by_id(self, subaccount_id: str) -> Optional[Account]: ...
    @property
    def parent(self) -> Optional[Account]: ...
    @parent.setter
    def parent(self, value: Account) -> None: ...
    @property
    def color(self) -> str: ...
    @color.setter
    def color(self, value: str) -> None: ...
    @property
    def notes(self) -> str: ...
    @notes.setter
    def notes(self, value: str) -> None: ...
    @property
    def hidden(self) -> bool: ...
    @hidden.setter
    def hidden(self, value: bool) -> None: ...
    @property
    def placeholder(self) -> bool: ...
    @placeholder.setter
    def placeholder(self, value: bool) -> None: ...
    def get_account_guids(self, account_guids: Optional[List[str]]=...) -> List[str]: ...

class BankAccount(Account):
    type: Any = ...
    def __init__(self) -> None: ...

class IncomeAccount(Account):
    type: Any = ...
    def __init__(self) -> None: ...

class AssetAccount(Account):
    type: Any = ...
    def __init__(self) -> None: ...

class CreditAccount(Account):
    type: Any = ...
    def __init__(self) -> None: ...

class ExpenseAccount(Account):
    type: Any = ...
    def __init__(self) -> None: ...

class EquityAccount(Account):
    type: Any = ...
    def __init__(self) -> None: ...

class LiabilityAccount(Account):
    type: Any = ...
    def __init__(self) -> None: ...

class InterestAccountBase(abc.ABC, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def starting_date(self) -> datetime: ...
    @property
    @abc.abstractmethod
    def interest_percentage(self) -> Decimal: ...
    @property
    @abc.abstractmethod
    def payment_amount(self) -> Decimal: ...
    @property
    @abc.abstractmethod
    def starting_balance(self) -> Decimal: ...
    @abc.abstractmethod
    def get_info_at_date(self, date: datetime) -> LoanStatus: ...
    @abc.abstractmethod
    def get_all_payments(self, skip_additional_payments: bool=...) -> List[Tuple[datetime, Decimal, Decimal]]: ...

class InterestAccount(InterestAccountBase):
    additional_payments: Any = ...
    skip_payment_dates: Any = ...
    interest_start_date: Any = ...
    def __init__(self, starting_balance: Decimal, starting_date: datetime, interest_percentage: Decimal, payment_amount: Decimal, additional_payments: Optional[List[LoanExtraPayment]]=..., skip_payment_dates: Optional[List[datetime]]=..., interest_start_date: Optional[datetime]=...) -> Any: ...
    @property
    def starting_date(self) -> datetime: ...
    @starting_date.setter
    def starting_date(self, new_starting_date: datetime) -> None: ...
    @property
    def interest_percentage(self) -> Decimal: ...
    @interest_percentage.setter
    def interest_percentage(self, new_interest_percentage: Decimal) -> None: ...
    @property
    def payment_amount(self) -> Decimal: ...
    @payment_amount.setter
    def payment_amount(self, new_payment_amount: Decimal) -> None: ...
    @property
    def starting_balance(self) -> Decimal: ...
    @starting_balance.setter
    def starting_balance(self, new_starting_balance: Decimal) -> None: ...
    def get_info_at_date(self, date: datetime) -> LoanStatus: ...
    def get_all_payments(self, skip_additional_payments: bool=...) -> List[Tuple[datetime, Decimal, Decimal]]: ...

class InterestAccountWithSubaccounts(InterestAccountBase):
    additional_payments: Any = ...
    skip_payment_dates: Any = ...
    subaccounts: Any = ...
    def __init__(self, subaccounts: List[InterestAccount], additional_payments: Optional[List[Dict[str, Union[Decimal, datetime]]]]=..., skip_payment_dates: Optional[List[datetime]]=...) -> Any: ...
    @property
    def starting_date(self) -> datetime: ...
    @property
    def interest_percentage(self) -> Decimal: ...
    @property
    def payment_amount(self) -> Decimal: ...
    @property
    def starting_balance(self) -> Decimal: ...
    def get_info_at_date(self, date: datetime) -> LoanStatus: ...
    def get_all_payments(self, skip_additional_payments: bool=...) -> List[Tuple[datetime, Decimal, Decimal]]: ...
