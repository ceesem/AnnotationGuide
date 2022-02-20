import jsonschema
import attrs
import pandas as pd

SPATIAL_POINT_CLASSES = ["SpatialPoint", "BoundSpatialPoint"]


class AnnotationGuide(object):
    def __init__(self, schema, name=None, update=False):
        """AnnotationGuide object, which helps produce a

        Parameters
        ----------
        schema : dict
            JSONschema object.
        name : _type_, optional
            _description_, by default None
        update : bool, optional
            _description_, by default False
        """
        self._schema = schema
        self._update = update
        self._classes = [x for x in schema["definitions"].keys()]
        self._ref_class = schema.get("$ref").split("/")[-1]

        if name is None:
            self.name = self._ref_class
        else:
            self.name = name

        self._required_props = (
            schema["definitions"].get(self._ref_class).get("required")
        )
        self._spatial_pts = {}
        self._convert_pts = {}
        self._props = []
        class_props = schema.get("definitions").get(self._ref_class).get("properties")
        for prop in class_props:
            if "$ref" in class_props.get(prop):
                if (
                    class_props.get(prop)["$ref"].split("/")[-1]
                    in SPATIAL_POINT_CLASSES
                ):
                    self._spatial_pts[prop] = f"{prop}_position"
                    self._convert_pts[f"{prop}_position"] = prop
            self._props.append(prop)
        self._prop_names = self._name_positions()

        self._anno_list = []

        self.add = self._make_anno_func(
            id_field=self._update, mixin=(self._build_mixin(),)
        )

    def __repr__(self):
        nanno = len(self._anno_list)
        if self._update:
            update = "Update"
        else:
            update = "New"
        return f"{update} annotation helper for {self.name} with {nanno} annotations."

    @property
    def update(self):
        return self._update

    @property
    def fields(self):
        if self.update:
            return ["id"] + self._prop_names
        else:
            return self._prop_names

    @property
    def annotations(self):
        return [self._process_annotation(a, flat=False) for a in self._anno_list]

    @property
    def annotation_dataframe(self):
        return pd.DataFrame.from_records(
            [self._process_annotation(a, flat=True) for a in self._anno_list],
        )

    def _process_annotation(self, anno, flat=False):
        dflat = attrs.asdict(anno, filter=lambda a, v: v is not None)
        if flat:
            return dflat
        else:
            return self._unflatten_spatial_points(dflat)

    def _build_mixin(self):
        class AddAndValidate(object):
            def __attrs_post_init__(inner_self):
                jsonschema.validate(self._process_annotation(inner_self), self._schema)
                if self._update:
                    if "id" not in d:
                        raise jsonschema.ValidationError(
                            '"id" field must be in annotation.'
                        )
                    if not isinstance(d.get("id"), int):
                        raise jsonschema.ValidationError(
                            '"id" field must be an integer.'
                        )
                self._anno_list.append(inner_self)

        return AddAndValidate

    def _make_anno_func(self, id_field=False, mixin=()):
        c = {}
        if id_field:
            c["id"] = attrs.field()
        for prop, prop_name in zip(self._props, self._prop_names):
            if prop in self._required_props:
                c[prop_name] = attrs.field()
            else:
                c[prop_name] = attrs.field(default=None)
        return attrs.make_class(self.name, c, bases=mixin)

    def _name_positions(self):
        return [
            x if x not in self._spatial_pts else f"{x}_position" for x in self._props
        ]

    def _unflatten_spatial_points(self, d):
        dout = {}
        for k, v in d.items():
            if k in self._convert_pts:
                dout[self._convert_pts[k]] = {"position": v}
            else:
                dout[k] = v
        return dout
