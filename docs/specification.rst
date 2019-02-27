Specification
=============

.. _binary:

Binary Representations
----------------------

Both schemas and communications are based on binary representations in remcall. The following rules apply to these representations:

- Primitive types in remcall are: ``void``, ``boolean``, ``int8``, ``uint8``, ``int16``, ``uint16``, ``int32``, ``uint32``, ``int64``, ``uint64``, ``float32``, ``float64``, ``string``, ``date``, ``time``, ``datetime``.
- Bytes are represented using ``uint8``.
- Arrays of values are represented using a ``uint32`` denoting the length and then all consecutive binary representations of the values.
- ``string`` values are encoded in UTF8 and then serialized as a byte-Array.
- Types are referenced using ``int32``; negative values reference an array of the type that is referenced using the positive number (arrays of arrays are not supported in remcall). Type references are never exchanged in a remcall communication, they are relevant only within the schema.
- Methods are referenced using one of the *unsigned* integer types, the schema specifies which one to use.
- Objects are referenced using one of the *signed* integer types, the schema specifies which one to use; negative values indicate that the implementation resides on the client (and is proxied on the server), positive values indicate that the implementation resides on the server (and is proxied on the client).
- The pseudo-type ``name`` is used in this document (but does not actually exist in remcall); it denotes a ``string`` that contains only characters from 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789' and does not start with a number; such names should be usable as variable or type names in all modern programming languages.
- Binary values will usually be displayed using their hexadecimal representation in this document which will be indicated using a leading "0x", e.g. 0xff to display a ``uint8`` with value 255; longer sequences of binary data will be split into blocks of 4 bytes = 8 hex characters, e.g. 0x00000001 0x00000002 0x00000003; if binary values exhibit a useful string representation, this will be used instead of hexadecimal values.

.. _schema:

Schema Definition
-----------------

Schemas in remcall exhibit a canonical binary representation. This feature allows to identify schemas uniquely using a cryptographic hash (sha256) of that representation.
Upon initiating a remcall communication this hash value is exchanged between the two parties to ensure that the same schema is employed on both sides.

.. raw:: html

    <table>
    <thead>
        <tr>
        <th>Type</th>
        <th>Title</th>
        <th>Description</th>
        <th>Example / Constant Value<th>
        <tr>
    </thead>
    <tbody>
        <tr>
        <td><code>byte[7]</code></td>
        <td>Magic constant</td>
        <td>Marking the following stream of data as remcall related</td>
        <td>REMCALL</td>
        </tr>
        <tr>
        <td><code>byte[6]</code></td>
        <td>Magic schema constant</td>
        <td>Marking the following stream of data as a remcall schema (as opposed to a remcall communication)</td>
        <td>SCHEMA</td>
        </tr>
        <tr>
        <td><code>string</code></td>
        <td>Schema label</td>
        <td>Free text label for the schema; for informational purposes only, may or may not be reflected in the compiled code</td>
        <td>A nice schema</td>
        </tr>
        <tr>
        <div class="anchor" id="bytes-method-ref"></div>
        <td><code>uint32</code></td>
        <td>Number of bytes for method references</td>
        <td>During communication, methods are identified using unsigned integers of this length, allowed values are 1, 2, 4 and 8; should be checked against the number of available methods in the schema by the compiler</td>
        <td>0x00000002</td>
        </tr>
        <tr>
        <td><code>uint32</code></td>
        <td>Number of bytes for object references</td>
        <td>During communication, objects are identified using signed integers of this length, allowed values are 1, 2, 4 and 8; note that this number is a runtime restriction on the number of objects, using 1 restricts the number of possible object references to 128 on both client and server</td>
        <td>0x00000004</td>
        </tr>
        <tr>
        <td><code>uint32</code></td>
        <td>Number of enums</td>
        <td>Number of enum declarations to be read in the following</td>
        <td>0x00000002</td>
        </tr>
        <tr>
        <td><code>uint32</code></td>
        <td>Number of records</td>
        <td>Number of record declarations to be read in the following</td>
        <td>0x00000001</td>
        </tr>
        <tr>
        <td><code>uint32</code></td>
        <td>Number of interfaces</td>
        <td>Number of interface declarations to be read in the following</td>
        <td>0x00000001</td>
        </tr>
        <tr>
        <td>...</td>
        <td><a href="#enums">Enum declarations</a></td>
        <td></td>
        <td></td>
        </tr>
        <tr>
        <td>...</td>
        <td><a href="#records">Record declarations</a></td>
        <td></td>
        <td></td>
        </tr>
        <tr>
        <td>...</td>
        <td><a href="#interfaces">Interface declarations</a></td>
        <td></td>
        <td></td>
        </tr>
        <tr>
        <td><code>byte[32]</code></td>
        <td>sha256 hash of schema</td>
        <td>sha256 hash of schema</td>
        <td>0xf3b73b5a 0x9f6294c4 0xa8b6b6f1 0x3b9dd129 0x9e5e9152 0xcf256a31 0xe3d13867 0x7a0fcb61</td>
        </tr>
    </tbody>
    </table>


.. _enums:

Declaration of Enums
--------------------

The following table defines the declaration of enums in remcall. The example values correspond to an enum called ``Status`` with possible values ``ON`` and ``OFF``.

.. raw:: html

    <table>
    <thead>
        <tr>
        <th>Type</th>
        <th>Title</th>
        <th>Description</th>
        <th>Example / Constant Value<th>
        <tr>
    </thead>
    <tbody>
        <tr>
        <td><code>uint8</code></td>
        <td>Declare enum constant</td>
        <td>Marking the following stream of data as an enum declaration</td>
        <td>0x02</td>
        </tr>
        <tr>
        <td><code>int32</code></td>
        <td>Type reference for this enum</td>
        <td>ID by which this enum type can be referenced in the schema</td>
        <td>0x00000021</td>
        </tr>
        <tr>
        <td><code>name</code></td>
        <td>Name for this enum</td>
        <td>Type name for this enum used in target languages</td>
        <td>Status</td>
        </tr>
        <tr>
        <td><code>uint32</code></td>
        <td>Number of possible enum values</td>
        <td>Number of possible values this enum can take</td>
        <td>0x00000003</td>
        </tr>
        <tr>
        <td><code>name[]</code></td>
        <td>Possible values for this enum</td>
        <td>Sequence of <code>name</code> payloads that will be possible values for this enum</td>
        <td>0x00000002 0x00000002 ON 0x00000003 OFF</td>
        </tr>
    </tbody>
    </table>


.. _records:

Declaration of Records
----------------------

The following table defines the declaration of records in remcall.

.. raw:: html

    <table>
    <thead>
        <tr>
        <th>Type</th>
        <th>Title</th>
        <th>Description</th>
        <th>Example / Constant Value<th>
        <tr>
    </thead>
    <tbody>
        <tr>
        <td><code>uint8</code></td>
        <td>Declare record constant</td>
        <td>Marking the following stream of data as a record declaration</td>
        <td>0x03</td>
        </tr>
        <tr>
        <td><code>int32</code></td>
        <td>Type reference for this record</td>
        <td>ID by which this record type can be referenced in the schema</td>
        <td>0x00000022</td>
        </tr>
        <tr>
        <td><code>name</code></td>
        <td>Name for this record</td>
        <td>Type name for this record used in target languages</td>
        <td>Address</td>
        </tr>
        <tr>
        <td><code>uint32</code></td>
        <td>Number of record fields</td>
        <td>Number of fields this record type contains</td>
        <td>0x00000002</td>
        </tr>
        <tr>
        <td>...</td>
        <td><a href="#record-fields">Field declarations</a></td>
        <td>Sequence (of length as defined by previous <code>uint32</code>) of type-name pairs describing individual record fields</td>
        <td></td>
        </tr>
    </tbody>
    </table>

.. _record-fields:

The following table describes the field declarations within a record.  This declaration works exactly the same way as `method argument declarations`__.

__ method-args_

.. raw:: html

    <table>
    <thead>
        <tr>
        <th>Type</th>
        <th>Title</th>
        <th>Description</th>
        <th>Example / Constant Value<th>
        <tr>
    </thead>
    <tbody>
        <tr>
        <td><code>int32</code></td>
        <td>Type reference for this field</td>
        <td>References a type (primitive or complex)</td>
        <td>0x0000000C</td>
        </tr>
        <tr>
        <td><code>name</code></td>
        <td>Name for this field</td>
        <td>Field name used in target languages</td>
        <td>Street</td>
        </tr>
    </tbody>
    </table>


.. _interfaces:

Declaration of Interfaces
-------------------------

The following table defines the declaration of interfaces in remcall.

.. raw:: html

    <table>
    <thead>
        <tr>
        <th>Type</th>
        <th>Title</th>
        <th>Description</th>
        <th>Example / Constant Value<th>
        <tr>
    </thead>
    <tbody>
        <tr>
        <td><code>uint8</code></td>
        <td>Declare interface constant</td>
        <td>Marking the following stream of data as an interface declaration</td>
        <td>0x04</td>
        </tr>
        <tr>
        <td><code>int32</code></td>
        <td>Type reference for this interface</td>
        <td>ID by which this interface type can be referenced in the schema</td>
        <td>0x00000023</td>
        </tr>
        <tr>
        <td><code>name</code></td>
        <td>Name for this interface</td>
        <td>Type name for this interface used in target languages</td>
        <td>User</td>
        </tr>
        <tr>
        <td><code>uint32</code></td>
        <td>Number of methods</td>
        <td>Number of methods this interface type contains</td>
        <td>0x00000005</td>
        </tr>
        <tr>
        <td>...</td>
        <td><a href="#methods">Method declarations</a></td>
        <td>Sequence (of length as defined by previous <code>uint32</code>) of method declarations</td>
        <td></td>
        </tr>
    </tbody>
    </table>

.. _methods:

The following table describes the method declarations within an interface.

.. raw:: html

    <table>
    <thead>
        <tr>
        <th>Type</th>
        <th>Title</th>
        <th>Description</th>
        <th>Example / Constant Value<th>
        <tr>
    </thead>
    <tbody>
        <tr>
        <td><code>uint8</code>, <code>uint16</code>, <code>uint32</code> or <code>uint64</code></td>
        <td>Method reference</td>
        <td>Reference to this method; exact type is defined in schema header by <a href="#bytes-method-ref">Number of bytes for method references</a></td>
        <td>0x09</td>
        </tr>
        <tr>
        <td><code>name</code></td>
        <td>Name for this method</td>
        <td>Method name used in target languages</td>
        <td>SetName</td>
        </tr>
        <tr>
        <td><code>uint32</code></td>
        <td>Number of arguments</td>
        <td>Number of arguments this method expects</td>
        <td>0x00000001</td>
        </tr>
        <tr>
        <td>...</td>
        <td><a href="#method-args">Method arguments</a></td>
        <td>Sequence (of length as defined by previous <code>uint32</code>) of type-name pairs describing individual arguments</td>
        <td></td>
        </tr>
    </tbody>
    </table>

.. _method-args:

The following table describes the argument declarations within a method. This declaration works exactly the same way as `record field declarations`__.

__ record-fields_

.. raw:: html

    <table>
    <thead>
        <tr>
        <th>Type</th>
        <th>Title</th>
        <th>Description</th>
        <th>Example / Constant Value<th>
        <tr>
    </thead>
    <tbody>
        <tr>
        <td><code>int32</code></td>
        <td>Type reference for this argument</td>
        <td>References a type (primitive or complex)</td>
        <td>0x0000000C</td>
        </tr>
        <tr>
        <td><code>name</code></td>
        <td>Name for this argument</td>
        <td>Argument name used in target languages</td>
        <td>name</td>
        </tr>
    </tbody>
    </table>

.. _communication:

Communication Protocol
----------------------

.. _implementation:

Implementation Guidelines
-------------------------

.. _examples:

Examples
--------