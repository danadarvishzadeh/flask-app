from flask import current_app, g, request, jsonify


class PaginatorBase:
    
    filters = None
    query_set = None
    schema = None
    model = None
    output_name = None
    per_page = 5

    @classmethod
    def get_data_set(cls):
        if cls.query_set is not None:
            return cls.query_set
        data = cls.model.query
        if cls.filters is not None:
            data = data.filter_by(**cls.filters)
        return data

    @classmethod
    def return_page(cls, page, callback):
        pagination = cls.get_data_set().paginate(page, per_page=cls.per_page, error_out=False)
        data = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for(callback, page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for(callback, page=page+1, _external=True)
        output_name = cls.model.__name__.lower() + 's' if cls.output_name is None else cls.output_name
        return jsonify({
        output_name: cls.schema.dump(data, many=True),
        'prev': prev,
        'next': next,
        'count': pagination.total
        })