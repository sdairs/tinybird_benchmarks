SELECT count(), toStartOfHour(left(record.time_us::Nullable(String), -6)::DateTime) AS time 
FROM bluesky_json
GROUP BY time