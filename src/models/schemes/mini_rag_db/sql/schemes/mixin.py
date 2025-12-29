class DictMixin:
    def dict(self, by_alias=False, exclude_none=False):
        # Base data from columns
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        # Handle additional properties if defined in subclass overrides or if needed
        # For now, generic column iteration is sufficient for DB schema mirroring

        # Handle alias (id -> _id)
        if by_alias and "id" in data:
            data["_id"] = data.pop("id")

        # exclude_none
        if exclude_none:
            return {k: v for k, v in data.items() if v is not None}
        return data
