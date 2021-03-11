SELECT j.name, s.step_id, s.step_name,
  s.last_run_date, s.last_run_time, h.message
FROM dbo.sysjobs AS j
  JOIN dbo.sysjobsteps AS s
    ON j.job_id = s.job_id
  JOIN dbo.sysjobhistory AS h
    ON h.job_id = j.job_id
      AND h.step_id = s.step_id
      AND h.run_date = s.last_run_date
      AND h.run_time = s.last_run_time
WHERE 1 = 1
  AND j.enabled = 1
  AND s.last_run_outcome = 0
  AND s.last_run_date != 0;
