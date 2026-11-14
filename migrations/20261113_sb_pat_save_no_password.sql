-- PAT Predictor Save without a password (AB, 13 Nov 2026: "just a simple save button and anyone who uses it last can
-- save it"). Replaces the password-checked save of 20261113_sb_pat_input_saves.sql.
-- APPLIED 13 Nov 2026 (AB: "Yes, go ahead"), as migration sb_pat_save_no_password, without this file's begin /
-- commit. Checked: out-of-range values and an unknown broker are refused; a save inside a rolled-back transaction
-- returned ok, wrote the rows and logged the Save.
--
-- What it does, step by step:
--   1. Drops public.sb_save_pat_inputs(broker, inputs, password) and creates public.sb_save_pat_inputs(broker, inputs):
--      the same value checks (growth −50 % … +100 % a quarter, P/E above 0 and up to 200, discounts 0 … 100 %), the
--      same upsert of the broker's sb_assumptions rows and the same log in sb_input_saves (with the rows each Save
--      replaced, so any Save can be undone). The last Save wins. A light guard against a runaway script: at most 30
--      Saves a minute across all brokers (private.sb_save_attempts keeps one row per Save).
--   2. Drops the password pieces: private.sb_set_save_password and private.sb_save_secret (empty; no password was set).
-- Unchanged: public.sb_pat_saved_inputs, public.sb_input_saves, Groww's pat_mtf_qoq_growth row.
-- Rolling back = re-run steps 2 and 5–6 of 20261113_sb_pat_input_saves.sql and drop the new function.

begin;

drop function public.sb_save_pat_inputs(text, jsonb, text);

create function public.sb_save_pat_inputs(p_broker text, p_inputs jsonb)
returns jsonb
language plpgsql
volatile
security definer
set search_path = public, private
as $$
declare
  recent   int;
  g        numeric;
  gm       numeric;
  disc     numeric;
  today    numeric;
  pe       numeric[];
  prev     jsonb;
  src      text := 'PAT Predictor page Save, ' || to_char(now() at time zone 'Asia/Kolkata', 'DD Mon YYYY HH24:MI') || ' IST';
begin
  if not exists (select 1 from public.sb_brokers where broker_id = p_broker) then
    return jsonb_build_object('ok', false, 'error', 'unknown broker');
  end if;
  select count(*) into recent from private.sb_save_attempts where at > now() - interval '1 minute';
  if recent >= 30 then
    return jsonb_build_object('ok', false, 'error', 'Too many saves in the last minute: try again shortly');
  end if;
  begin
    g := (p_inputs ->> 'g')::numeric;
    gm := (p_inputs ->> 'gm')::numeric;
    disc := (p_inputs ->> 'disc')::numeric;
    today := (p_inputs ->> 'today')::numeric;
    pe := array(select jsonb_array_elements_text(p_inputs -> 'pe')::numeric);
  exception when others then
    g := null;
  end;
  if g is null or gm is null or disc is null or today is null or pe is null or array_length(pe, 1) is distinct from 3
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

revoke all on function public.sb_save_pat_inputs(text, jsonb) from public;
grant execute on function public.sb_save_pat_inputs(text, jsonb) to anon, authenticated;

drop function private.sb_set_save_password(text);
drop table private.sb_save_secret;

commit;
