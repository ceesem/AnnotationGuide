from .base import AnnotationGuide

__version__ = "0.0.0"


def build_annotation_guide(
    client, table_name=None, schema_name=None, update=False, id_field=False
):
    """Build an annotation guide for a schema or table.

    Parameters
    ----------
    client : client.CAVEclient
        Initialized cave client
    table_name : string, optional
        Table name in the materialization database, by default None. If provided, uses the schema for the table. Either table_name or schema_name must be provided.
    schema_name : string, optional
        Schema name in the schema service, by default None. If table_name is also provided, it is used instead of schema name. Either table name or schema name must be provided.
    update : bool, optional
        Specifies if the annotations will be updates rather than new annotations. Updated annotations need an additional id column to be set. By default False.

    Returns
    -------
    AnnotationGuide
    """
    if table_name is not None:
        obj_name = table_name
        schema_name = client.materialize.get_table_metadata(table_name)["schema"]
    else:
        if schema_name is None:
            raise ValueError("Must specify either table name or schema name")
        obj_name = schema_name
    schema = client.schema.schema_definition(schema_name)
    return AnnotationGuide(
        schema,
        name=obj_name,
        update=update,
        id_field=id_field,
    )
