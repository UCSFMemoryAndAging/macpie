.. currentmodule:: macpie

Dataset
=======

A ``Dataset`` is a tabular data structure that contains columns representing common
data associated with clinical research:

* ``id_col_name`` to represent record IDs
* ``date_col_name`` to represent record collection dates
* ``id2_col_name`` to represent a secondary id column, most commonly a patient/subject ID.

Constructor
-----------
.. autosummary::
   :toctree: api/

   Dataset


Column changes
--------------
Methods related to changing the columns in the Dataset.

.. autosummary::
   :toctree: api/
   
    Dataset.create_id_col
    Dataset.rename_col
    Dataset.prepend_level
    Dataset.drop_sys_cols
    Dataset.keep_cols
    Dataset.keep_fields


Binary operator functions
-------------------------
.. autosummary::
   :toctree: api/

   date_proximity
   group_by_keep_one


Reshaping, sorting
------------------
.. autosummary::
   :toctree: api/

   Dataset.sort_by_id2


Excel IO
--------
Serialization to and from Excel requires an ``excel_dict``, which
is a dict that contains the needed information to round-trip a Dataset.

.. autosummary::
   :toctree: api/
   
   Dataset.cross_section
   Dataset.display_name_generator
   Dataset.to_excel_dict
   Dataset.from_excel_dict


Helpers
-------

.. autosummary::
   :toctree: api/
   
   DatasetFields


Subclasses
----------

.. autosummary::
   :toctree: api/
   
   LavaDataset
