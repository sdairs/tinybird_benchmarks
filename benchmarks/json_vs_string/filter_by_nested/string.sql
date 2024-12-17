SELECT count()
FROM bluesky_strings
where collection = 'commit' and JSONExtract(record, 'commit', 'operation', 'String') == 'create'