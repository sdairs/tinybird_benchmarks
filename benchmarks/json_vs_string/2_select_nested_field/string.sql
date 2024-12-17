select JSONExtract(record, 'did', 'String') as did from bluesky_strings
LIMIT 100000