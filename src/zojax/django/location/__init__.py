

class AlreadyRegistered(Exception):
    """
    An attempt was made to register a model more than once.
    """
    pass


registry = []


def register(model, location_descriptor_attr='location'):
    """
    Sets the given model class up for working with categories.
    """

    from zojax.django.location.managers import LocationDescriptor

    if model in registry:
        raise AlreadyRegistered("The model '%s' has already been "
            "registered." % model._meta.object_name)
    if hasattr(model, location_descriptor_attr):
        raise AttributeError("'%s' already has an attribute '%s'. You must "
            "provide a custom location_descriptor_attr to register." % (
                model._meta.object_name,
                location_descriptor_attr,
            )
        )

    # Add location descriptor
    setattr(model, location_descriptor_attr, LocationDescriptor())

    # Finally register in registry
    registry.append(model)
