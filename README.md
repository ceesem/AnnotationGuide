# AnnotationGuide

Get some help when generating annotations for the CAVE framework.

In the CAVE framework, annotations go in tables and each table has a schema, or a specific format that annotations must follow.
AnnotationGuide uses information about the table you are posting to and makes sure that your annotations abide by the schema, plus offers hints about how to format data.

## Installation

Install from pypi with `pip install annotation_guide`.

## How to use

### Initializing an AnnotationGuide

The simplest way to initialize an AnnotationGuide to upload new annotations just needs the name of an annotation table or a specific schema using the helper function `build_annotation_guide`.
This approach uses the CAVEclient to find and download the schema, so you need to initialize this first.
Let's say you have a table called `"my_cell_types"` that you want to post annotations to.

```python
import annotation_guide as ag
from caveclient import CAVEclient

client = CAVEclient('my_datastack') # Change this, of course!
table_name = "my_cell_types"
guide = ag.build_annotation_guide(client, table_name=table_name)
```

Alternatively, if you know the name of the schema you want (for example, `"cell_type_local"`), you can use that directly.

```python
schema_name = "cell_type_local"
guide = ag.build_annotation_guide(client, schema_name=schema_name)
```

Finally, if you have the full JSONschema (for example, downloaded from the schema service), you can pass this directly to the AnnotationGuide class instead of using the helper function.

```python
schema = client.schema.schema_definition(schema_name)
guide = ag.AnnotationGuide(schema=schema)
```

### Adding New Annotations

Annotations are added to the guide object, which stores a list of annotations.

```python
guide.add(
    cell_type="pyramidal_cell",
    classification_system="neuron",
    pt_position=[1234, 4567, 8910],
)
```

The annotation is validated against the schema immediately, so if anything is incorrect it will be flagged.
Note that previously added annotations don't need to be re-added.
The annotation guide list can be cleared with `guide.clear_annotations()`.

The function hints on `guide.add` will let you know the fields that can be added.
Any fields that are optional will have default values set to None.

### Checking and posting annotations

The collection of annotations can be seen in one of two ways:

* `guide.annotations` returns a list of dicts, with one element per annotation. The formatting is correct for passing immediately to the `client.annotation.post_annotation` function.
* `guide.annotation_dataframe` returns a dataframe with one row per annotation and a column for each field. This could be particularly useful for looking over a list of annotations before posting.

### Updating annotations or specifying annotation ids

When updating an existing annotation, the annotation service requires an annotation id in addition to the other data being correctly specified.
If you want to generate annotations for an update to the guide, set the flag `update=True` when building it.
For example:

```python
upgrade_guide = ag.build_annotation_guide(client, table_name=table_name, upgrade=True)
```

When adding annotations to the guide afterward, the first element will always be the `id`:

```python
upgrade_guide.add(
    id = 1434,
    cell_type="basket_cell",
    classification_system="neuron",
    pt_position=[1234, 4567, 8910],
)
```

Annotation IDs can also be specified for new annotations, although this use requires care.
Nonetheless, using the flag `id_field=True` will achieve the same results as `upgrade=True`.
