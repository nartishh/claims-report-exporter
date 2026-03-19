SELECT event_no,
       event_type,
       create_date
FROM claims_event
WHERE trunc(create_date) = trunc(SYSDATE - 1)
ORDER BY event_no