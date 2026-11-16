-- 10 Nov 2026: an on-time trigger for the daily job's night runs (.github/workflows/daily.yml, src/live/gate.py).
-- NOT YET APPLIED. Needs AB's OK (CLAUDE.md rule 7) and the GitHub token below, which AB adds himself.
--
-- Why: trading day D should be on the dashboard before 06:00 IST on D+1. ExchangesDash publishes D's MCX contract count
-- only after MCX closes (23:30-23:55 IST), so the 19:47 IST run can't have D, and GitHub's own schedule has started the
-- daily job 6-9 hours late (9 Nov 2026: the 19:47 IST run started at 04:55 IST). pg_cron in this project starts the job's
-- night runs on time through GitHub's workflow_dispatch API, with input night=true. Each night run refreshes the market
-- rows and stops unless a later day than the latest published one is complete, so a night with nothing new adds nothing.
-- No sb_* table changes; nothing is copied by the ExchangesDash mirror (it copies sb_* tables only).
--
-- Step 0 (AB, before applying; not in this file): create a fine-grained GitHub personal access token
--   github.com → Settings → Developer settings → Fine-grained tokens → Generate new token
--   Resource owner abiyani-tools · Repository access: only abiyani-tools/brokersdashboard
--   Permissions → Repository → Actions: Read and write (nothing else) · Expiration: e.g. 1 year (note the date)
-- and store it in this project's Vault from the SQL editor (the token never goes in a file, a commit or a chat):
--   select vault.create_secret('<the token>', 'github_dispatch_token', 'workflow_dispatch of brokersdashboard daily.yml (night runs)');
--
-- What this file does, step by step:
--   1. Turns on pg_net (HTTP requests from SQL) and pg_cron (a scheduler inside Postgres). Both are Supabase-supported.
--   2. Creates private.dispatch_daily_night_run(): reads the token from Vault and POSTs
--      {"ref": "main", "inputs": {"night": "true"}} to the daily workflow's dispatches endpoint. In schema `private`, which
--      the REST API does not expose, and only the postgres role can run it.
--   3. Schedules it at 22:15 and 23:15 UTC, Mon-Fri (pg_cron runs in UTC): 03:45 and 04:45 IST, Tue-Sat, so Monday's to
--      Friday's trading days are covered.
--
-- Check after applying:
--   select private.dispatch_daily_night_run();             -- starts a night run now; it stops at the gate if nothing is new
--   select id, status_code, content from net._http_response order by id desc limit 3;   -- 204 = GitHub accepted it
--   select jobname, schedule, active from cron.job;
--   select jobid, status, return_message, start_time from cron.job_run_details order by start_time desc limit 5;
-- Undo:
--   select cron.unschedule('daily-night-run-0345-ist'); select cron.unschedule('daily-night-run-0445-ist');
--   drop function private.dispatch_daily_night_run();
--   delete from vault.secrets where name = 'github_dispatch_token';   -- then revoke the token on GitHub

create extension if not exists pg_net;
create extension if not exists pg_cron;

create schema if not exists private;
revoke all on schema private from public, anon, authenticated;

create or replace function private.dispatch_daily_night_run() returns bigint
language plpgsql
security definer
set search_path = ''
as $$
declare
  token text;
  request_id bigint;
begin
  select decrypted_secret into token from vault.decrypted_secrets where name = 'github_dispatch_token';
  if token is null then
    raise exception 'Vault secret github_dispatch_token is missing (step 0 of migrations/20261110_night_run_trigger.sql)';
  end if;
  select net.http_post(
    url := 'https://api.github.com/repos/abiyani-tools/brokersdashboard/actions/workflows/daily.yml/dispatches',
    headers := jsonb_build_object(
      'Authorization', 'Bearer ' || token,
      'Accept', 'application/vnd.github+json',
      'X-GitHub-Api-Version', '2022-11-28',
      'User-Agent', 'brokers-dashboard-night-run',
      'Content-Type', 'application/json'),
    body := jsonb_build_object('ref', 'main', 'inputs', jsonb_build_object('night', 'true'))
  ) into request_id;
  return request_id;
end;
$$;

revoke all on function private.dispatch_daily_night_run() from public, anon, authenticated;

select cron.schedule('daily-night-run-0345-ist', '15 22 * * 1-5', 'select private.dispatch_daily_night_run()');
select cron.schedule('daily-night-run-0445-ist', '15 23 * * 1-5', 'select private.dispatch_daily_night_run()');
