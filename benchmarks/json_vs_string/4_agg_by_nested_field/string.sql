SELECT count(), toStartOfHour(left(JSONExtract(record, 'time_us', 'String'), -6)::DateTime) AS time 
FROM bluesky_strings
GROUP BY time