"""Managers for OAuth models."""

from django.db import models

from readthedocs.core.querysets import NoReprQuerySet


class RelatedUserQuerySet(NoReprQuerySet, models.QuerySet):

    """For models with relations through :py:class:`User`."""

    def api(self, user=None):
        """Return objects for user."""
        if not user.is_authenticated:
            return self.none()
        return self.filter(users=user)


class RemoteRepositoryQuerySet(RelatedUserQuerySet):
    pass


class RemoteOrganizationQuerySet(RelatedUserQuerySet):
    pass
