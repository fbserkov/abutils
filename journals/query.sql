SELECT *
FROM mng.journal
WHERE is_error = 1
  AND date_journal > DATEADD (DAY, -1, GETDATE());
