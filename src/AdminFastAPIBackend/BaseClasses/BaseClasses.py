"""
Pydantic provides various constraints and validation features for string, integer, float, and other types. Let's go through the most commonly used constraints:

### 1. Strings (`constr`):

- `min_length`: Minimum length of the string.
- `max_length`: Maximum length of the string.
- `regex`: Validates the string with the provided regular expression.
- `strip_whitespace`: If `True`, leading and trailing whitespaces are stripped.
- `curtail_length`: If a string exceeds the `max_length`, it will truncate it to this length.

Example:

```python
from pydantic import constr

name: constr(min_length=2, max_length=10, regex=r'^[a-zA-Z]+$')
```

### 2. Integers (`conint`):

- `gt`: Greater than a specific value.
- `ge`: Greater than or equal to a specific value.
- `lt`: Less than a specific value.
- `le`: Less than or equal to a specific value.
- `multiple_of`: Must be a multiple of the specified value.

Example:

```python
from pydantic import conint

age: conint(gt=0, lt=120)
```

### 3. Floats (`confloat`):

Similar to `conint` but for floating point numbers:

- `gt`
- `ge`
- `lt`
- `le`
- `multiple_of`

Example:

```python
from pydantic import confloat

price: confloat(gt=0.0)
```

### 4. Lists (`conlist`):

- `min_items`: Minimum number of items.
- `max_items`: Maximum number of items.

Example:

```python
from pydantic import conlist

numbers: conlist(int, min_items=1, max_items=10)
```

### 5. Others:

- `EmailStr`: Validate string as a valid email address.
- `UrlStr`: Validate string as a valid URL.
- `Hostname`: Validate string as a valid hostname.
- `IPvAnyAddress`: Validate string as a valid IPv4 or IPv6 address.
- `PositiveInt`: Validate as a positive integer.
- `NegativeInt`: Validate as a negative integer.
- `PositiveFloat`: Validate as a positive float.
- `NegativeFloat`: Validate as a negative float.

### 6. Enums:

Enums can be used to limit a value to a specific set of allowed values:

```python
from enum import Enum
from pydantic import BaseModel

class ColorEnum(str, Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"

class Model(BaseModel):
    color: ColorEnum
```

### 7. Validators:

In addition to the above constraints, you can also define custom validation logic using the `@validator` decorator:

```python
from pydantic import BaseModel, validator

class UserModel(BaseModel):
    name: str
    age: int

    @validator('age')
    def check_age(cls, v):
        if v <= 0:
            raise ValueError('Age must be positive')
        return v
```

These are just some of the many constraints and validations that Pydantic offers. For more in-depth details, refer to
    the [official Pydantic documentation](https://pydantic-docs.helpmanual.io/).
"""
import re
from typing import Literal

from pydantic import Field, BaseModel, constr

from src.logger import setup_logger

# from pydantic import BaseModel as _BaseModel

logger = setup_logger(__name__)

IDType = constr(min_length=1, max_length=100, strip_whitespace=True)
EmailType = constr(min_length=2, max_length=50, regex=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                   strip_whitespace=True)
PhoneNuberType = constr(min_length=2, max_length=15, regex=r'^[0-9-+() ]+$', strip_whitespace=True)
PasswordType = constr(min_length=8, max_length=50, regex=r'^[a-zA-Z0-9_.+-]+$', strip_whitespace=True)

class CoreModel(BaseModel):
    """
    Core base model with basic fields and common validation. Models that inherit this class should implement
    their own `set_id` method.

    Attributes
    ----------
    id : str, optional
        The ID of the model instance. By default, it's None.
    status : str, optional
        The status of the model instance, which can be "active", "inactive", or "archived".
        By default, it's "inactive".

    Methods
    -------
    set_id() -> str:
        Abstract method to get the ID of the model instance.
    """
    id: IDType = Field(None, hidden=True)
    status: Literal["active", "inactive", "archived"] = Field("inactive", hidden=True)

    class Config:
        """Here so fields can be hidden from the OPENAPI schema if hidden=True. Value can still be used as normal."""

        @staticmethod
        def schema_extra(schema: dict, _):
            props = {}
            for k, v in schema.get('properties', {}).items():
                if not v.get("hidden", False):
                    props[k] = v
            schema["properties"] = props


def validate_id_constraints(id_str):
    """As per Firestore Rules and Limitations for Collections and Documents id's"""
    # Use IDType
    try:
        if id_str is None:
            raise ValueError("The id_str cannot be None.")
        id_str = IDType(id_str)
    except Exception as e:
        raise ValueError(f"Invalid id_str: {e}")

    # Check if string is valid UTF-8
    try:
        id_str = id_str.encode('utf-8').decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("The id_str is not a valid UTF-8 string.")

    # Check byte length
    if len(id_str.encode('utf-8')) > 1500:
        raise ValueError("The id_str must be no longer than 1,500 bytes.")

    # Check for forward slash
    if '/' in id_str:
        raise ValueError("The id_str cannot contain a forward slash (/).")

    # Check for single or double periods
    if id_str == '.' or id_str == '..':
        raise ValueError("The id_str cannot solely consist of a single period (.) or double periods (..).")

    # Check regular expression __.*__
    if re.match(r'^__.*__$', id_str):
        raise ValueError("The id_str cannot match the regular expression __.*__.")

    # Check for pattern __id[0-9]+__
    if re.match(r'^__id\d+__$', id_str):
        raise ValueError("The id_str cannot match the pattern __id[0-9]+__.")

    return id_str


def validate_and_correct_dictionary(dict_to_verify: dict, default_config: dict, log=None) -> tuple:
    """
    Verifies that the given JSON config contains all the required keys as per the default config.
    If not, adds the missing keys with the default values.
    Returns a log of warnings and errors in case of missing or unknown keys.

    :param dict_to_verify: The JSON configuration to verify.
    :type dict_to_verify: dict
    :param default_config: The default configuration used for verification.
    :type default_config: dict
    :param log: A list of log messages. Default is an empty list.
    :type log: list, optional
    :return: A tuple of the verified JSON configuration and the log of warnings/errors.
    :rtype: tuple

    Usage::

        json_config = {
            "key1": "value1",
            "key2": {
                "subkey1": "subvalue1"
            }
        }

        default_config = {
            "key1": "value1",
            "key2": {
                "subkey1": "subvalue1",
                "subkey2": "subvalue2"
            },
            "key3": "value3"
        }

        verified_config, log = verify_configuration_keys(json_config, default_config)
        # verified_config will contain all keys from default_config, and log will contain warning/error messages
    """
    if log is None:
        log = []
    if not dict_to_verify:
        dict_to_verify = {}

    for key, value in default_config.items():
        if key not in dict_to_verify:
            dict_to_verify[key] = value
            log.append(f'Warning: Missing key "{key}" has been added with default value "{value}"')
        elif isinstance(value, dict):
            if isinstance(dict_to_verify[key], dict):
                dict_to_verify[key], log = validate_and_correct_dictionary(dict_to_verify[key], value, log)
            else:
                log.append(f'Error: Key "{key}" should contain a dictionary but found "{type(dict_to_verify[key])}"')
        else:
            if not isinstance(dict_to_verify[key], type(value)):
                log.append(
                    f'Error: Key "{key}" should be of type "{type(value)}" but found "{type(dict_to_verify[key])}"')

    for key in dict_to_verify.keys():
        if key not in default_config:
            log.append(f'Error: Unknown key "{key}" found in config')

    return dict_to_verify, log
