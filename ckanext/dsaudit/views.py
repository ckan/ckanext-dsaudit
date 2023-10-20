from flask import Blueprint
from flask.views import MethodView

from ckan.plugins import toolkit as tk

dsaudit = Blueprint('dsaudit', __name__)

@dsaudit.route('/dataset/<id>/resource/<resource_id>/ds-activity')
def resource_activity(id, resource_id):
    after = tk.request.args.get("after")
    before = tk.request.args.get("before")
    activity_type = tk.request.args.get("activity_type")

    context = {'for_view': True, 'auth_user_obj': tk.g.userobj}
    limit = _get_activity_stream_limit()
    activity_types = [activity_type] if activity_type else None

    try:
        activity_dict = {
            "id": resource_id,
            "after": after,
            "before": before,
            # ask for one more just to know if this query has more results
            "limit": limit + 1,
            "activity_types": activity_types,
        }
        activity_stream = tk.get_action("resource_activity_list")(
            context, activity_dict
        )
    except tk.ObjectNotFound:
        return tk.abort(404, tk._("Resource not found"))
    except tk.NotAuthorized:
        return tk.abort(403, tk._("Unauthorized to read resource %s") % id)
    except tk.ValidationError:
        return tk.abort(400, tk._("Invalid parameters"))

    has_more = len(activity_stream) > limit
    # remove the extra item if exists
    if has_more:
        if after:
            activity_stream.pop(0)
        else:
            activity_stream.pop()

    older_activities_url = _get_older_activities_url(
        has_more,
        activity_stream,
        id=id,
        activity_type=activity_type,
        resource_id=resource_id,
        )

    newer_activities_url = _get_newer_activities_url(
        has_more,
        activity_stream,
        id=id,
        activity_type=activity_type,
        resource_id=resource_id,
    )

    try:
        # resource_edit_base template uses these
        pkg_dict = tk.get_action(u'package_show')({}, {u'id': id})
        resource = tk.get_action(u'resource_show')({}, {u'id': resource_id})

    except (tk.ObjectNotFound, tk.NotAuthorized):
        tk.abort(404, _(u'Resource not found'))

    return tk.render(
        "dsaudit/resource_activity.html",
        {
            "activity_stream": activity_stream,
            "id": resource_id,
            "limit": limit,
            "has_more": has_more,
            "activity_type": activity_type,
            "newer_activities_url": newer_activities_url,
            "older_activities_url": older_activities_url,
            "pkg_dict": pkg_dict,
            "resource": resource,
        },
    )


def _get_activity_stream_limit():
    base_limit = tk.config.get("ckan.activity_list_limit", 31)
    max_limit = tk.config.get("ckan.activity_list_limit_max", 100)
    return min(base_limit, max_limit)


def _get_older_activities_url(has_more, stream, **kwargs):
    """ Returns pagination's older activities url.

    If "after", we came from older activities, so we know it exists.
    if "before" (or is_first_page), we only show older activities if we know
    we have more rows
    """
    after = tk.request.args.get("after")
    before = tk.request.args.get("before")
    is_first_page = after is None and before is None
    url = None
    if after or (has_more and (before or is_first_page)):
        before_time = datetime.fromisoformat(
            stream[-1]["timestamp"]
        )
        url = tk.h.url_for(
            tk.request.endpoint,
            before=before_time.timestamp(),
            **kwargs
        )

    return url


def _get_newer_activities_url(has_more, stream, **kwargs):
    """ Returns pagination's newer activities url.

    if "before", we came from the newer activities, so it exists.
    if "after", we only show newer activities if we know
    we have more rows
    """
    after = tk.request.args.get("after")
    before = tk.request.args.get("before")
    url = None

    if before or (has_more and after):
        after_time = datetime.fromisoformat(
            stream[0]["timestamp"]
        )
        url = tk.h.url_for(
            tk.request.endpoint,
            after=after_time.timestamp(),
            **kwargs
        )
    return url

