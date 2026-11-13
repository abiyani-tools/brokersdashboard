-- PAT Predictor inputs that the dashboard page saves (AB, 13 Nov 2026): the reader edits the broking and MTF QoQ ADR
-- growth, the P/E per scenario and the two discounts on the PAT tab, presses Save, and the values become the broker's
-- sb_assumptions rows, which the engine reads on its next run (so the published PAT and valuation lines use them) and
-- which the page shows again on every visit until changed.
-- APPLIED 13 Nov 2026 (AB: "Yes, apply it"), as migration sb_pat_input_saves, without this file's begin / commit
-- (the migration tool wraps it in its own transaction). The security advisor's "SECURITY DEFINER function executable
-- by anon / authenticated" warnings for the two public functions are intended: they are the page's only way in, and
-- the save is gated by the password, the rate limit and the value checks.
--
-- What it does, step by step:
--   1. Seeds GROWW's pat_mtf_qoq_growth = 12.7% (AB: add about Rs 500 Cr of MTF book a quarter; 500 ÷ start book
--      3,939 = 12.7%). Angel One has no row, so its MTF keeps growing at its broking rate until a Save writes one.
--   2. Creates schema `private` (no grants to anon / authenticated, so the API cannot read it) with
--        private.sb_save_secret    one row: the bcrypt hash of the Save password (pgcrypto, never the password)
--        private.sb_save_attempts  every Save attempt (time, broker, ok), for the rate limit
--   3. Creates public.sb_input_saves: one row per successful Save (broker, time, the inputs written, the rows they
--      replaced). Public read like the other sb_* tables, so the history is visible and any Save can be undone.
--   4. Creates public.sb_pat_saved_inputs(broker): the broker's current inputs (its own row, else the '*' row; MTF
--      growth falls back to the broking rate) and the latest Save. SECURITY DEFINER because sb_assumptions has RLS on
--      and no read policy; it returns only these five keys.
--   5. Creates public.sb_save_pat_inputs(broker, inputs, password): checks the password against the hash, refuses
--      after 5 failed attempts in 15 minutes, validates every value (growth −50 % … +100 % a quarter, P/E 0 … 200,
--      discounts 0 … 100 %), upserts the broker's own rows (a '*' row such as pat_discount_fwd is not changed: the
--      broker gets its own row that overrides it), logs the Save and returns the saved inputs. It writes nothing else.
--      Errors come back as {ok: false, error} instead of an exception, so the failed attempt is still logged.
--   6. Creates private.sb_set_save_password(password): AB runs it once in the SQL editor to set (or change) the
--      password; no API role can call it.
-- Rolling back:
--   drop function public.sb_save_pat_inputs(text, jsonb, text); drop function public.sb_pat_saved_inputs(text);
--   drop table public.sb_input_saves; drop schema private cascade;
--   delete from public.sb_assumptions where broker_id = 'GROWW' and key = 'pat_mtf_qoq_growth';
--   (and restore any row a Save changed from sb_input_saves.previous)

begin;

-- 1. Groww's MTF growth
insert into public.sb_assumptions (broker_id, key, value, value_text, unit, source_ref, note)
values ('GROWW', 'pat_mtf_qoq_growth', 0.127, null, 'per quarter',
        'AB instruction, 13 Nov 2026: add about Rs 500 Cr of MTF book a quarter',
        'MTF ADR grows by this each quarter from the start MTF ADR, like broking at pat_adr_qoq_growth. 12.7% = Rs 500 Cr ÷ the start book Rs 3,939 Cr (start MTF ADR Rs 2.3903 Cr/day × 247 days ÷ 14.99% yield, run of 11 Nov 2026). Input: edit on the PAT page and Save, or here.')
on conflict (broker_id, key) do nothing;

-- 2. private schema
create schema if not exists private;
revoke all on schema private from public, anon, authenticated;

create table private.sb_save_secret (
  id        int         primary key default 1 check (id = 1),
  pass_hash text        not null,
  set_at    timestamptz not null default now()
);

create table private.sb_save_attempts (
  at        timestamptz not null default now(),
  broker_id text,
  ok        boolean     not null
);

-- 3. history of Saves
create table public.sb_input_saves (
  id        bigint generated always as identity primary key,
  broker_id text        not null references public.sb_brokers (broker_id),
  saved_at  timestamptz not null default now(),
  inputs    jsonb       not null,
  previous  jsonb       not null
);
alter table public.sb_input_saves enable row level security;
create policy public_read on public.sb_input_saves for select to anon, authenticated using (true);
revoke insert, update, delete, truncate on public.sb_input_saves from anon, authenticated;

-- 4. read the current inputs
create function public.sb_pat_saved_inputs(p_broker text)
returns jsonb
language sql
stable
security definer
set search_path = public
as $$
  with a as (
    select distinct on (key) key, value, value_text, broker_id
    from public.sb_assumptions
    where broker_id in ('*', p_broker)
      and key in ('pat_adr_qoq_growth', 'pat_mtf_qoq_growth', 'pat_pe', 'pat_discount_fwd', 'pat_discount_today')
    order by key, (broker_id = p_broker) desc
  ), last as (
    select saved_at from public.sb_input_saves where broker_id = p_broker order by saved_at desc limit 1
  )
  select jsonb_build_object(
    'broker', p_broker,
    'g',      (select value from a where key = 'pat_adr_qoq_growth'),
    'gm',     coalesce((select value from a where key = 'pat_mtf_qoq_growth'), (select value from a where key = 'pat_adr_qoq_growth')),
    'gm_own', exists (select 1 from a where key = 'pat_mtf_qoq_growth'),
    'pe',     (select to_jsonb(string_to_array(value_text, ',')::numeric[]) from a where key = 'pat_pe'),
    'disc',   (select value from a where key = 'pat_discount_fwd'),
    'today',  (select value from a where key = 'pat_discount_today'),
    'saved_at', (select saved_at from last))
  where exists (select 1 from public.sb_brokers where broker_id = p_broker);
$$;

-- 5. save
create function public.sb_save_pat_inputs(p_broker text, p_inputs jsonb, p_password text)
returns jsonb
language plpgsql
volatile
security definer
set search_path = public, private, extensions
as $$
declare
  h        text;
  fails    int;
  g        numeric := (p_inputs ->> 'g')::numeric;
  gm       numeric := (p_inputs ->> 'gm')::numeric;
  disc     numeric := (p_inputs ->> 'disc')::numeric;
  today    numeric := (p_inputs ->> 'today')::numeric;
  pe       numeric[];
  prev     jsonb;
  src      text := 'PAT Predictor page Save, ' || to_char(now() at time zone 'Asia/Kolkata', 'DD Mon YYYY HH24:MI') || ' IST';
begin
  if not exists (select 1 from public.sb_brokers where broker_id = p_broker) then
    return jsonb_build_object('ok', false, 'error', 'unknown broker');
  end if;
  select pass_hash into h from private.sb_save_secret where id = 1;
  if h is null then
    return jsonb_build_object('ok', false, 'error', 'Saving is not set up yet: the password has not been set');
  end if;
  select count(*) into fails from private.sb_save_attempts where not ok and at > now() - interval '15 minutes';
  if fails >= 5 then
    return jsonb_build_object('ok', false, 'error', 'Too many wrong passwords: try again in 15 minutes');
  end if;
  if p_password is null or crypt(p_password, h) <> h then
    insert into private.sb_save_attempts (broker_id, ok) values (p_broker, false);
    return jsonb_build_object('ok', false, 'error', 'Wrong password');
  end if;
  begin
    pe := array(select jsonb_array_elements_text(p_inputs -> 'pe')::numeric);
  exception when others then
    pe := null;
  end;
  if g is null or gm is null or disc is null or today is null or pe is null or array_length(pe, 1) <> 3
     or g not between -0.5 and 1 or gm not between -0.5 and 1 or disc not between 0 and 1 or today not between 0 and 1
     or exists (select 1 from unnest(pe) x where x <= 0 or x > 200) then
    return jsonb_build_object('ok', false, 'error',
      'Values out of range: growth −50 % to +100 % a quarter, P/E above 0 and up to 200, discounts 0 to 100 %');
  end if;

  select coalesce(jsonb_agg(to_jsonb(s) order by s.key), '[]'::jsonb) into prev
  from public.sb_assumptions s
  where s.broker_id = p_broker
    and s.key in ('pat_adr_qoq_growth', 'pat_mtf_qoq_growth', 'pat_pe', 'pat_discount_fwd', 'pat_discount_today');

  insert into public.sb_assumptions as t (broker_id, key, value, value_text, unit, source_ref, note)
  values (p_broker, 'pat_adr_qoq_growth', g, null, 'per quarter', src, 'Broking (and cash) ADR growth a quarter. Saved on the PAT page.'),
         (p_broker, 'pat_mtf_qoq_growth', gm, null, 'per quarter', src, 'MTF ADR growth a quarter. Saved on the PAT page.'),
         (p_broker, 'pat_pe', null, array_to_string(pe, ','), 'x (bear,base,bull)', src, 'P/E bear, base, bull. Saved on the PAT page.'),
         (p_broker, 'pat_discount_fwd', disc, null, 'fraction', src, 'Discount FY28 → FY27. Saved on the PAT page.'),
         (p_broker, 'pat_discount_today', today, null, 'fraction', src, 'Discount FY27 → today. Saved on the PAT page.')
  on conflict (broker_id, key) do update
    set value = excluded.value, value_text = excluded.value_text, unit = excluded.unit,
        source_ref = excluded.source_ref, note = excluded.note;

  insert into private.sb_save_attempts (broker_id, ok) values (p_broker, true);
  insert into public.sb_input_saves (broker_id, inputs, previous)
  values (p_broker, jsonb_build_object('g', g, 'gm', gm, 'pe', to_jsonb(pe), 'disc', disc, 'today', today), prev);
  return jsonb_build_object('ok', true, 'saved', public.sb_pat_saved_inputs(p_broker));
end;
$$;

revoke all on function public.sb_pat_saved_inputs(text) from public;
revoke all on function public.sb_save_pat_inputs(text, jsonb, text) from public;
grant execute on function public.sb_pat_saved_inputs(text) to anon, authenticated;
grant execute on function public.sb_save_pat_inputs(text, jsonb, text) to anon, authenticated;

-- 6. set the password (AB, once, in the SQL editor): select private.sb_set_save_password('<password>');
create function private.sb_set_save_password(p text)
returns void
language sql
security definer
set search_path = private, extensions
as $$
  insert into private.sb_save_secret (id, pass_hash, set_at) values (1, crypt(p, gen_salt('bf')), now())
  on conflict (id) do update set pass_hash = excluded.pass_hash, set_at = excluded.set_at;
$$;
revoke all on function private.sb_set_save_password(text) from public, anon, authenticated;

commit;
