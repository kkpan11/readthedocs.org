"""Project version handling."""

import operator
import unicodedata

from bumpver.v2version import parse_version_info
from bumpver.version import PatternError
from packaging.version import InvalidVersion
from packaging.version import Version

from readthedocs.builds.constants import LATEST
from readthedocs.builds.constants import LATEST_VERBOSE_NAME
from readthedocs.builds.constants import STABLE
from readthedocs.builds.constants import STABLE_VERBOSE_NAME
from readthedocs.builds.constants import TAG
from readthedocs.vcs_support.backends import backend_cls


def parse_version_failsafe(version_string):
    """
    Parse a version in string form and return Version object.

    If there is an error parsing the string
    or the version doesn't have a "comparable" version number,
    ``None`` is returned.

    :param version_string: version as string object (e.g. '3.10.1')
    :type version_string: str or unicode

    :returns: version object created from a string object

    :rtype: packaging.version.Version
    """
    if not isinstance(version_string, str):
        uni_version = version_string.decode("utf-8")
    else:
        uni_version = version_string

    final_form = ""

    try:
        normalized_version = unicodedata.normalize("NFKD", uni_version)
        ascii_version = normalized_version.encode("ascii", "ignore")
        final_form = ascii_version.decode("ascii")
        return Version(final_form)
    except InvalidVersion:
        # Handle the special case of 1.x, 2.x or 1.0.x, 1.1.x
        if final_form and ".x" in final_form:
            # Replace the .x with .999999 so it's sorted last.
            final_form = final_form.replace(".x", ".999999")
            return parse_version_failsafe(final_form)
    except UnicodeError:
        pass

    return None


def comparable_version(version_string, repo_type=None):
    """
    Can be used as ``key`` argument to ``sorted``.

    The ``LATEST`` version shall always beat other versions in comparison.
    ``STABLE`` should be listed second. If we cannot figure out the version
    number then we sort it to the bottom of the list.

    If `repo_type` is given, it adds the default "master" version
    from the VCS (master, default, trunk).
    This version is sorted higher than LATEST and STABLE.

    :param version_string: version as string object (e.g. '3.10.1' or 'latest')
    :type version_string: str or unicode

    :param repo_type: Repository type from which the versions are generated.

    :returns: a comparable version object (e.g. 'latest' -> Version('99999.0'))

    :rtype: packaging.version.Version
    """
    highest_versions = []
    if repo_type:
        backend = backend_cls.get(repo_type)
        if backend and backend.fallback_branch:
            highest_versions.append(backend.fallback_branch)
    highest_versions.extend([LATEST_VERBOSE_NAME, STABLE_VERBOSE_NAME])

    comparable = parse_version_failsafe(version_string)
    if not comparable:
        if version_string in highest_versions:
            position = highest_versions.index(version_string)
            version_number = str(999999 - position)
            comparable = Version(version_number)
        else:
            comparable = Version("0.01")
    return comparable


def sort_versions(version_list):
    """
    Take a list of Version models and return a sorted list.

    This only considers versions with comparable version numbers.
    It excludes versions like "latest" and "stable".

    :param version_list: list of Version models
    :type version_list: list(readthedocs.builds.models.Version)

    :returns: sorted list in descending order (latest version first) of versions

    :rtype: list(tupe(readthedocs.builds.models.Version,
            packaging.version.Version))
    """
    versions = []
    # use ``.iterator()`` to avoid fetching all the versions at once (this may
    # have an impact when the project has lot of tags)
    for version_obj in version_list.iterator():
        version_slug = version_obj.verbose_name
        comparable_version = parse_version_failsafe(version_slug)
        if comparable_version:
            versions.append((version_obj, comparable_version))

    # sort in-place to avoid leaking memory on projects with lot of versions
    versions.sort(
        key=lambda version_info: version_info[1],
        reverse=True,
    )
    return versions


def determine_stable_version(version_list):
    """
    Determine a stable version for version list.

    :param version_list: list of versions
    :type version_list: list(readthedocs.builds.models.Version)

    :returns: version considered the most recent stable one or ``None`` if there
              is no stable version in the list

    :rtype: readthedocs.builds.models.Version
    """
    versions = sort_versions(version_list)
    versions = [
        (version_obj, comparable)
        for version_obj, comparable in versions
        if not comparable.is_prerelease
    ]

    if versions:
        # We take preference for tags over branches. If we don't find any tag,
        # we just return the first branch found.
        for version_obj, comparable in versions:
            if version_obj.type == TAG:
                return version_obj

        version_obj, comparable = versions[0]
        return version_obj
    return None


def sort_versions_generic(
    version_list,
    exception,
    parse_version,
    latest_stable_at_beginning,
    raw_pattern=None,
):
    """
    Sort Read the Docs versions based on ``parse_version`` function.

    ``parse_version`` function is called with ``slug`` and ``raw_pattern`` as arguments to decide how to sort them.

    All versions that raise ``exception`` are added at the end sorted alphabetically.
    """

    alphabetically_sorted_version_list = sorted(
        version_list,
        key=operator.attrgetter("slug"),
        reverse=True,
    )

    initial_versions = []
    valid_versions = []
    invalid_versions = []
    for version in alphabetically_sorted_version_list:
        if latest_stable_at_beginning:
            if version.slug in (STABLE, LATEST):
                initial_versions.append((version, version.slug))
                continue

        try:
            valid_versions.append(
                (
                    version,
                    parse_version(
                        slug=version.slug,
                        raw_pattern=raw_pattern,
                    ),
                )
            )
        except exception:
            # When the version is invalid, we put it at the end while keeping
            # the alphabetically sorting between the invalid ones.
            invalid_versions.append((version, None))

    all_versions = (
        # It relies on the version list sorted alphabetically first ("l" comes first than "s")
        sorted(initial_versions, key=operator.itemgetter(1))
        + sorted(valid_versions, key=operator.itemgetter(1), reverse=True)
        + invalid_versions
    )
    return [item[0] for item in all_versions if item[0] is not None]


def sort_versions_python_packaging(version_list, latest_stable_at_beginning):
    """
    Sort Read the Docs versions list using ``packaging`` algorithm.

    All the invalid version (raise ``InvalidVersion``) are added at the end
    sorted alphabetically.

    https://pypi.org/project/packaging/
    https://packaging.python.org/en/latest/specifications/version-specifiers/
    """

    def parse_version(*args, slug=None, **kwargs):
        return Version(slug)

    return sort_versions_generic(
        version_list,
        InvalidVersion,
        parse_version,
        latest_stable_at_beginning,
    )


def sort_versions_custom_pattern(version_list, raw_pattern, latest_stable_at_beginning):
    """
    Sort Read the Docs versions using a custom pattern.

    All the invalid version (raise ``PatternError``) are added at the end
    sorted alphabetically.

    It uses ``Bumpver`` behinds the scenes for the parsing and sorting.
    https://github.com/mbarkhau/bumpver
    """

    def parse_version(*args, slug=None, raw_pattern=None, **kwargs):
        return parse_version_info(slug, raw_pattern=raw_pattern)

    return sort_versions_generic(
        version_list,
        PatternError,
        parse_version,
        latest_stable_at_beginning,
        raw_pattern,
    )


def sort_versions_calver(version_list, latest_stable_at_beginning):
    """
    Sort Read the Docs versions using CalVer pattern: ``YYYY.0M.0M``.

    All the invalid version are added at the end sorted alphabetically.
    """
    raw_pattern = "YYYY.0M.0D"
    return sort_versions_custom_pattern(
        version_list,
        raw_pattern,
        latest_stable_at_beginning,
    )
