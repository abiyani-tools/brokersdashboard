-- 14 Nov 2026 (AB): close the open Save until it is gated.
-- Review on sucaanalytics-max/ExchangesDash#91: sb_save_pat_inputs is SECURITY DEFINER and anon could execute it, so
-- anyone holding the publishable key could rewrite a broker's PAT inputs in sb_assumptions. Only service_role (the
-- engine / CI) can call it now; the page's Save is split out of #91 and comes back gated in a later PR.
-- Applied to everjfpbnlbcpuarnhob on 14 Nov 2026 as migration sb_pat_save_revoke_anon (sb_input_saves had 0 rows).
revoke execute on function public.sb_save_pat_inputs(text, jsonb) from public, anon, authenticated;
grant execute on function public.sb_save_pat_inputs(text, jsonb) to service_role;
