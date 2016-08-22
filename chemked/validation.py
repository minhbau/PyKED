"""Validation functions for values.

Based on validation module of pyrk (https://github.com/pyrk).

.. moduleauthor:: Kyle Niemeyer <kyle.niemeyer@gmail.com>
"""

# Python 2 compatibility
from __future__ import print_function
from __future__ import division
import sys

import pkg_resources
try:
    import ruamel.yaml as yaml
except ImportError:
    import yaml

import pint
from cerberus import Validator

# Local imports
from .utils import units

if sys.version_info > (3,):
    long = int

# Load the ChemKED schema definition file
schema_file = pkg_resources.resource_filename(__name__, 'chemked_schema.yaml')
with open(schema_file, 'r') as f:
    schema = yaml.safe_load(f)

# These top-level keys in the schema server as references for lower-level keys.
# They are removed to prevent conflicts due to required variables, etc.
for key in ['author', 'value-unit-required', 'value-unit-optional', 'composition', 'ignition-type']:
    schema.pop(key)

# SI units for available value-type properties
property_units = {'temperature': 'kelvin',
                  'pressure': 'pascal',
                  'ignition-delay': 'second',
                  'pressure-rise': '1.0 / second',
                  'compression-time': 'second',
                  'volume': 'meter**3',
                  'time': 'second',
                  }

class OurValidator(Validator):
    """Custom validator with rules for units and Quantities.
    """
    def _validate_isvalid_unit(self, isvalid_unit, field, value):
        """Checks for appropriate units.
        """
        if isvalid_unit:
            quantity = 1.0 * units(value['units'])
            try:
                quantity.to(property_units[field])
            except pint.DimensionalityError:
                self._error(field, 'incompatible units; should be consistent '
                            'with ' + property_units[field]
                            )

    def _validate_isvalid_quantity(self, isvalid_quantity, field, value):
        """Checks for valid given value and appropriate units.
        """
        if isvalid_quantity:
            quantity = value['value'] * units(value['units'])
            low_lim = 0.0 * units(property_units[field])

            try:
                if quantity <= low_lim:
                    self._error(field, 'value must be > 0.0')
            except pint.DimensionalityError:
                self._error(field, 'incompatible units; should be consistent '
                            'with ' + property_units[field]
                            )


def validate_geq(value_name, value, low_lim):
    """Raise error if value lower than specified lower limit or wrong type.

    Parameters
    ---------
    value_name : str
        Name of value being tested
    value : int, float, numpy.ndarray, pint.Quantity
        Value to be tested
    low_lim : type(value)
        Lowest acceptable limit of ``value``

    Returns
    -------
    value : type(value)
        The original value

    """

    try:
        if validate_num(value_name, value) < low_lim:
            msg = (value_name + ' must be greater than or equal to ' +
                   str(low_lim) + '.\n'
                   'Value provided was: ' + str(value)
                   )
            # RuntimeError used to avoid being caught by Pint comparison error.
            # Pint should really raise TypeError (or something) rather than
            # ValueError.
            raise RuntimeError(msg)
        else:
            return value
    except ValueError:
        if isinstance(value, units.Quantity):
            msg = ('\n' + value_name + ' given with units, when variable '
                   'should be dimensionless.'
                   )
            raise pint.DimensionalityError(value.units, None,
                                           extra_msg=msg
                                           )
        else:
            msg = ('\n' + value_name + ' not given in units. '
                   'Correct units share dimensionality with: ' +
                   str(low_lim.units)
                   )
            raise pint.DimensionalityError(None, low_lim.units,
                                           extra_msg=msg
                                           )
    except pint.DimensionalityError:
        msg = ('\n' + value_name + ' given in incompatible units. '
               'Correct units share dimensionality with: ' +
               str(low_lim.units)
               )
        raise pint.DimensionalityError(value.units, low_lim.units,
                                       extra_msg=msg
                                       )
    except:
        raise


def validate_gt(value_name, value, low_lim):
    """Raise error if value not greater than lower limit or wrong type.

    Parameters
    ---------
    value_name : str
        Name of value being tested
    value : int, float, numpy.ndarray, pint.Quantity
        Value to be tested
    low_lim : type(value)
        ``value`` must be greater than this limit

    Returns
    -------
    value : type(value)
        The original value

    """

    try:
        if not validate_num(value_name, value) > low_lim:
            msg = (value_name + ' must be greater than ' +
                   str(low_lim) + '.\n'
                   'Value provided was: ' + str(value)
                   )
            # RuntimeError used to avoid being caught by Pint comparison error.
            # Pint should really raise TypeError (or something) rather than
            # ValueError.
            raise RuntimeError(msg)
        else:
            return value
    except ValueError:
        if isinstance(value, units.Quantity):
            msg = ('\n' + value_name + ' given with units, when variable '
                   'should be dimensionless.'
                   )
            raise pint.DimensionalityError(value.units, None,
                                           extra_msg=msg
                                           )
        else:
            msg = ('\n' + value_name + ' not given in units. '
                   'Correct units share dimensionality with: ' +
                   str(low_lim.units)
                   )
            raise pint.DimensionalityError(None, low_lim.units,
                                           extra_msg=msg
                                           )
    except pint.DimensionalityError:
        msg = ('\n' + value_name + ' given in incompatible units. '
               'Correct units share dimensionality with: ' +
               str(low_lim.units)
               )
        raise pint.DimensionalityError(value.units, low_lim.units,
                                       extra_msg=msg
                                       )
    except:
        raise


def validate_leq(value_name, value, upp_lim):
    """Raise error if value greater than specified upper limit or wrong type.

    Parameters
    ---------
    value_name : str
        Name of value being tested
    value : int, float, numpy.ndarray, pint.Quantity
        Value to be tested
    upp_lim : type(value)
        Highest acceptable limit of ``value``

    Returns
    -------
    value : type(value)
        The original value

    """

    try:
        if validate_num(value_name, value) > upp_lim:
            msg = (value_name + ' must be less than or equal to ' +
                   str(upp_lim) + '.\n'
                   'Value provided was: ' + str(value)
                   )
            # RuntimeError used to avoid being caught by Pint comparison error.
            # Pint should really raise TypeError (or something) rather than
            # ValueError.
            raise RuntimeError(msg)
        else:
            return value
    except ValueError:
        if isinstance(value, units.Quantity):
            msg = ('\n' + value_name + ' given with units, when variable '
                   'should be dimensionless.'
                   )
            raise pint.DimensionalityError(value.units, None,
                                           extra_msg=msg
                                           )
        else:
            msg = ('\n' + value_name + ' not given in units. '
                   'Correct units share dimensionality with: ' +
                   str(upp_lim.units)
                   )
            raise pint.DimensionalityError(None, upp_lim.units,
                                           extra_msg=msg
                                           )
    except pint.DimensionalityError:
        msg = ('\n' + value_name + ' given in incompatible units. '
               'Correct units share dimensionality with: ' +
               str(upp_lim.units)
               )
        raise pint.DimensionalityError(value.units, upp_lim.units,
                                       extra_msg=msg
                                       )
    except:
        raise


def validate_num(value_name, value):
    """Raise error if value is not a number.

    Parameters
    ---------
    value_name : str
        Name of value being tested
    value : int, float, numpy.ndarray, pint.Quantity
        Value to be tested

    Returns
    -------
    value : type(value)
        The original value

    """
    if isinstance(value, (int, long, float, units.Quantity)):
        return value
    else:
        try:
            if isinstance(value.magnitude, (int, long, float, units.Quantity)):
                return value
        except AttributeError:
            pass
    msg = (value_name + ' must be an integer, long, float, or Quantity. \n'
           'The value provided was of type ' + str(type(value)) + ' and '
           'value ' + str(value)
           )
    raise TypeError(msg)
