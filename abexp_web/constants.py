CSP = {
    'default-src': [
        "'self'",
        "https://stackpath.bootstrapcdn.com",
        "https://code.jquery.com",
        "https://cdn.jsdelivr.net",
        "https://cdnjs.cloudflare.com",
        "https://cdn.datatables.net"
    ],
    'img-src': [
        "'self'",
        "data:",
        "https://stackpath.bootstrapcdn.com",
        "https://cdnjs.cloudflare.com",
        "https://cdn.datatables.net"
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",
        "https://stackpath.bootstrapcdn.com",
        "https://cdnjs.cloudflare.com",
        "https://cdn.datatables.net"
    ],
    'script-src': [
        "'self'",
        "'unsafe-inline'",
        "https://code.jquery.com",
        "https://cdn.jsdelivr.net",
        "https://stackpath.bootstrapcdn.com",
        "https://cdn.datatables.net"
    ],
    'font-src': [
        "'self'",
        "https://cdnjs.cloudflare.com"
    ]
}

BINARY_MAP = {
    'Yes': True,
    'No': False
}
