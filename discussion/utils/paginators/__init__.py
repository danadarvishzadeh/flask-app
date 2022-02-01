from flask import jsonify, url_for


class BasePaginator:
    
    query_set = None
    schema = None
    model = None
    output_name = None
    per_page = 10
    filters = None

    def get_data_set(self):
        if self.query_set is not None:
            return self.query_set
        data = self.model.query
        if self.filters is not None:
            data = data.filter_by(**self.filters)
        return data

    def return_page(self, page, callback):
        pagination = self.get_data_set().paginate(page, per_page=self.per_page, error_out=False)
        data = pagination.items
        prev = None
        if pagination.has_prev:
            prev = url_for(callback, page=page-1, _external=True)
        next = None
        if pagination.has_next:
            next = url_for(callback, page=page+1, _external=True)
        output_name = self.model.__name__.lower() + 's' if self.output_name is None else self.output_name
        return jsonify({
        output_name: self.schema().dump(data, many=True),
        'prev': prev,
        'next': next,
        'count': pagination.total
        })