from enum import Enum, StrEnum
from typing import Callable

class ContractStatus(StrEnum):
    NIL = "NIL"
    OK = "OK"
    WARN = "WARN"
    ERR = "ERR"
    BROKEN = "BROKEN"

'''
простенькая реализация основных понятий программирования по контракту: пред- и пост-условий и статусов
от себя добавил статус-предупреждение (WARN)
расширять дальше статус ошибки смысла не вижу

для классов, которые будут поддерживать контракт, нужно наследоваться от Contract и 
при этом их методы нужно оборачивать в декоратор @Contract.on
в методах-наследниках нужно вызывать методы check_pre, check_post, check_warn 

если метод не обернут в декоратор @Contract.on -- будут выбрасываться исключения
    - ContractErrPreException -- при невыполнении предусловия
    - ContractErrPostException -- при невыполнении постусловия
    - ContractWarningException -- при невыполнении условия предупреждения
    
декоратор как раз нужен, чтобы ловить эти исключения и изменять по ним соответствующие статусы
(ERR для пред- и пост-условий, WARN для предупреждений)

Задел на будущее -- восстановление структуры после непройденного пост-условия
(абстрактный метод _repar_post)
В общем случае можно предложить полную резервную копию завернуть в отдельный декоратор, и в случае 
неуспешного прохождения пост-условия восстанавливаться из нее

Но это мне видится неэффективным, особенно для громоздких структур 
(условно, >10M -- на каждый чих не наздравствуешься)
Я это реализую, когда дойдут руки, но в общем случае надо оставить возможность переложить эту ответственность
на сам класс -- для многих структур есть более точные и изящные механизмы персистентности, которые не требуют
создания полной резервной копии структуры.

TODO: сделать наследника с deepcopy
TODO: сделать наследника с логгированием

заметка на полях: логгер можно захерачить просто как поле
'''

class ContractException(Exception):
    def __init__(self, message: str = ""):
        self._message = message
        
    def __str__(self):
        return "Unknown contract exception: " + self._message

class ContractWarningException(ContractException):
    def __str__(self):
        return "Contract warning: " + self._message

class ContractErrException(ContractException):
    def __str__(self):
        return "Contract error: " + self._message

class ContractErrPreException(ContractErrException):
    def __str__(self):
        return "Contract precondition error: " + self._message

class ContractErrPostException(ContractErrException):
    def __str__(self):
        return "Contract postcondition error: " + self._message


class Contract:
    def __init__(self):
        self._reset()

    def _reset(self):
        self._status = ContractStatus.NIL
        self._message = "NIL"
    
    def _check(self, condition: bool, exception: ContractException):
        if not condition:
            raise exception
        
        self._status = ContractStatus.OK
        self._message = "OK"
                
    def check_warn(self, condition: bool, message: str = ''):
        self._check(condition, ContractWarningException(message))
    
    def check_pre(self, condition: bool, message: str = ''):
        self._check(condition, ContractErrPreException(message))

    def check_post(self, condition: bool, message: str = ''):
        self._check(condition, ContractErrPostException(message))

    @property
    def message(self):
        return self._message
    
    def on(func):
        def inner(self, *args, **kwargs): 
            ans = None
            try:
                ans = func(self, *args, **kwargs)
                self._message = "OK"
                self._status = ContractStatus.OK
            except ContractWarningException as err:
                self._message = str(err) 
                self._status = ContractStatus.WARN
            except ContractErrPreException as ex:
                self._message = str(ex) 
                self._status = ContractStatus.ERR
            except ContractErrPostException as err:
                self._repair_post()
                self._message = str(err) 
                self._status = ContractStatus.BROKEN
            except:
                self._message = "UNKNOWN contract error"
                self._status = ContractStatus.BROKEN
            return ans
        return inner

    def _repair_post(self):
        pass

    @property
    def is_OK(self) -> bool:
        return self._status == ContractStatus.OK
    
    @property
    def is_WARN(self) -> bool:
        return self._status == ContractStatus.WARN
    
    @property
    def is_ERR(self) -> bool:
        return self._status == ContractStatus.ERR

    @property
    def is_BROKEN(self) -> bool:
        return self._status == ContractStatus.BROKEN