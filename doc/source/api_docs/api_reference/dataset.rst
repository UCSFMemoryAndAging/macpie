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

Serialization / IO / conversion
-------------------------------

.. autosummary::
   :toctree: api/

   Dataset.from_file
   Dataset.to_excel
   Dataset.to_excel_dict
   Dataset.from_excel_dict
   

All pandas ``DataFrame`` methods are also available.