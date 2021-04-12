def errorResponse(namespace, message, code=422):
    namespace.abort(code, message, status='failed')


def successResponse(message, code=200):
    return {
        'status': 'success',
        'message': message
    }, code