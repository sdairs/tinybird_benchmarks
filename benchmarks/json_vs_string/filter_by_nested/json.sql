SELECT count()
FROM bluesky_json
where collection = 'commit' and record.commit.operation == 'create'