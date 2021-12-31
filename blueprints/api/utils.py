from discussion.models import Discussion, Post, Invitation
from flask import current_app, url_for, jsonify
from .schemas import discussion_schema, post_schema, invitation_schema



def paginate_discussions(page, data_set, callback):
    pagination = data_set.paginate(page,
            per_page=current_app.config['DISCUSSION_DISCUSSIONS_PER_PAGE'],
            error_out=False)

    discussions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for(f'api.{callback}', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for(f'api.{callback}', page=page+1, _external=True)
    return jsonify({
    'discussions': discussion_schema.dump(discussions, many=True),
    'prev': prev,
    'next': next,
    'count': pagination.total
    })

def paginate_posts(page, data_set, callback):
    pagination = data_set.paginate(page,
            per_page=current_app.config['DISCUSSION_POSTS_PER_PAGE'],
            error_out=False)

    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for(f'api.{callback}', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for(f'api.{callback}', page=page+1, _external=True)
    return jsonify({
    'posts': post_schema.dump(posts, many=True),
    'prev': prev,
    'next': next,
    'count': pagination.total
    })


def paginate_invitatinos(page, data_set, callback):
    pagination = data_set.paginate(page,
            per_page=current_app.config['DISCUSSION_INVITATIONS_PER_PAGE'],
            error_out=False)

    invitions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for(f'api.{callback}', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for(f'api.{callback}', page=page+1, _external=True)
    return jsonify({
    'invitions': invitation_schema.dump(invitions, many=True),
    'prev': prev,
    'next': next,
    'count': pagination.total
    })