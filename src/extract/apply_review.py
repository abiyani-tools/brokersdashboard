"""Turn decisions from the review page into SQL for sb_disclosure_facts.

Input: a folder of JSON documents saved from the review page's `reviews` collection
(ArtifactData list with out_dir). Each document: {filing, decisions: {"f<fact_id>": {s, c, by, at}}}.

  approved -> status 'reviewed', reviewed_at = decision time
  flagged  -> stays 'staged'; the reviewer's note is appended to `note` so the figure can be re-read and corrected
  pending  -> no change

Usage: python3 apply_review.py <dir> > apply.sql   (then run the SQL against the brokers-dashboard project)
"""
import glob, json, os, sys


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def main(folder):
    approved, flagged = [], []
    for fn in sorted(glob.glob(os.path.join(folder, '**', '*.json'), recursive=True)):
        doc = json.load(open(fn))
        body = doc.get('data', doc)                    # tolerate either the raw body or a wrapped snapshot
        for key, d in (body.get('decisions') or {}).items():
            if not key.startswith('f') or not key[1:].isdigit():
                continue
            fid = int(key[1:])
            if d.get('s') == 'approved':
                approved.append((fid, d.get('at')))
            elif d.get('s') == 'flagged':
                flagged.append((fid, (d.get('c') or '').strip(), d.get('at')))
    out = ['begin;']
    for fid, at in approved:
        out.append(f"update sb_disclosure_facts set status='reviewed', reviewed_at={q(at)}::timestamptz "
                   f"where fact_id={fid} and status='staged' and extracted_by in ('parser','claude');")
    for fid, c, at in flagged:
        msg = f"Flagged on review page {at[:10] if at else ''}: {c or '(no note)'}"
        out.append(f"update sb_disclosure_facts set note=concat_ws(' · ', note, {q(msg)}) "
                   f"where fact_id={fid} and status='staged';")
    out.append('commit;')
    print('\n'.join(out))
    print(f'-- {len(approved)} approved, {len(flagged)} flagged', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1])
