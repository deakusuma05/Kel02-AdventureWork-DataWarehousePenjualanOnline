"""Run database checks only against an isolated MySQL instance in .audit-temp.

Example: python scripts/verify_database.py --mysql C:/path/bin/mysql.exe --port 13307
The server datadir MUST be a child of this repository's .audit-temp directory.
No operational schema is dropped or modified. Fresh audit_* schemas are retained.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
TABLES = {'dim_date': 'tanggal_key', 'dim_product': 'product_key',
          'dim_customer': 'customer_key', 'dim_territory': 'territory_key',
          'dim_promotion': 'promotion_key', 'dim_currency': 'currency_key',
          'dim_ship_method': 'ship_method_key', 'fact_online_sales': 'sales_detail_key'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mysql', required=True)
    parser.add_argument('--port', type=int, default=13307)
    args = parser.parse_args()
    base = [args.mysql, '--no-defaults', '--host=127.0.0.1', f'--port={args.port}',
            '--user=root', '--default-character-set=utf8mb4', '--batch', '--raw']
    def execute(sql, database=None, expected_error=None):
        cmd = base + ([f'--database={database}'] if database else [])
        p = subprocess.run(cmd, input=sql.encode('utf-8'), capture_output=True)
        out, err = p.stdout.decode('utf-8'), p.stderr.decode('utf-8', errors='replace')
        if expected_error:
            assert p.returncode != 0 and f'ERROR {expected_error} ' in err, (p.returncode, err)
            return err.strip()
        if p.returncode:
            raise RuntimeError(err)
        return out
    def rows(sql, database=None):
        out = execute(sql, database).strip().splitlines()
        return [dict(zip(out[0].split('\t'), row.split('\t'))) for row in out[1:]] if out else []
    info = rows('SELECT VERSION() AS version, @@datadir AS datadir, @@port AS port;')[0]
    datadir = Path(info['datadir']).resolve()
    assert datadir.is_relative_to((ROOT / '.audit-temp').resolve()), 'Refuse non-isolated server datadir'
    assert args.port != 3306, 'Refuse default operational port'
    stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    selected, legacy, target = (f'audit_new_{stamp}', f'audit_old_{stamp}', f'audit_ddl_{stamp}')
    for db in (selected, legacy, target):
        execute(f'CREATE DATABASE `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
    for source, db in [('sql/adventureworks_dw (2).sql', selected), ('sql/dump_adventureworks_dw.sql', legacy)]:
        dump = (ROOT / source).read_text(encoding='utf-8-sig').replace('`adventureworks_dw`', f'`{db}`')
        execute(dump, db)
    ddl = (ROOT / 'sql/ddl.sql').read_text(encoding='utf-8')
    execute(ddl, target)
    for table, key in TABLES.items():
        columns = rows(f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='{selected}' AND TABLE_NAME='{table}' ORDER BY ORDINAL_POSITION")
        names = ','.join('`'+c['COLUMN_NAME']+'`' for c in columns)
        execute(f'INSERT INTO `{table}` ({names}) SELECT {names} FROM `{selected}`.`{table}` WHERE `{key}` <> -1;', target)
    # Derive all days from the real dump's range; calendar records are not fabricated sales.
    execute("""INSERT INTO dim_date
SELECT CAST(DATE_FORMAT(d,'%Y%m%d') AS UNSIGNED), d, YEAR(d), IF(MONTH(d)<=6,1,2),
 QUARTER(d), MONTH(d), ELT(MONTH(d),'Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'),
 WEEKOFYEAR(d), DAY(d), DAYOFWEEK(d), ELT(DAYOFWEEK(d),'Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'), IF(DAYOFWEEK(d) IN(1,7),1,0)
FROM (SELECT DATE_ADD(bounds.lo, INTERVAL (a.n+b.n*10+c.n*100+e.n*1000) DAY) AS d, bounds.hi
 FROM (SELECT MIN(tanggal) lo, MAX(tanggal) hi FROM dim_date WHERE tanggal_key<>-1) bounds
 CROSS JOIN (SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a
 CROSS JOIN (SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) b
 CROSS JOIN (SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) c
 CROSS JOIN (SELECT 0 n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) e
) calendar WHERE d<=hi AND NOT EXISTS(SELECT 1 FROM dim_date existing WHERE existing.tanggal=calendar.d);""", target)
    def digest():
        return {table: hashlib.sha256(execute(f'SELECT * FROM `{table}` ORDER BY `{key}`', target).encode()).hexdigest() for table,key in TABLES.items()}
    before = digest()
    execute(ddl, target)
    after = digest()
    assert before == after, 'Repeated DDL changed loaded data'
    schemas = rows(f"SELECT TABLE_NAME,COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_KEY,EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA='{target}' ORDER BY TABLE_NAME,ORDINAL_POSITION")
    fks = rows(f"SELECT TABLE_NAME,COLUMN_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME FROM information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA='{target}' AND REFERENCED_TABLE_NAME IS NOT NULL")
    indexes = rows(f"SELECT TABLE_NAME,INDEX_NAME,COLUMN_NAME,NON_UNIQUE FROM information_schema.STATISTICS WHERE TABLE_SCHEMA='{target}' ORDER BY TABLE_NAME,INDEX_NAME,SEQ_IN_INDEX")
    assert len(fks) == 7
    assert len([i for i in indexes if i['INDEX_NAME']=='PRIMARY']) == 8
    unknown = {t: rows(f'SELECT COUNT(*) n FROM `{t}` WHERE `{k}`=-1', target)[0]['n'] for t,k in TABLES.items() if t != 'fact_online_sales'}
    assert set(unknown.values()) == {'1'}
    constraints = {}
    for file, code, marker in [('Pengujian-PK.sql',1062,'PRIMARY'),('pengujian-FK.sql',1452,'fk_fact_product'),('pengujian-NotNull.sql',1048,'line_total')]:
        error = execute((ROOT/'sql/pengujian'/file).read_text(encoding='utf-8'), target, code)
        assert marker in error
        constraints[file] = {'status':'LULUS','mysql_error':code,'message':error.replace(target,'audit_ddl_<run>')}
    assert before == digest(), 'Negative tests changed data'
    rebuild = (ROOT/'sql/ddl_rebuild.sql').read_text(encoding='utf-8')
    denied = execute(rebuild, target,1644)
    assert before == digest(), 'Denied rebuild changed data'
    rebuilt = f'audit_rebuild_{stamp}'
    execute(f'CREATE DATABASE `{rebuilt}`;')
    execute(ddl, rebuilt)
    execute('SET @confirm_dw_rebuild = DATABASE();\n'+rebuild, rebuilt)
    assert rows(f"SELECT COUNT(*) n FROM information_schema.TABLES WHERE TABLE_SCHEMA='{rebuilt}'")[0]['n']=='0'
    execute(ddl, rebuilt)
    def metrics(db):
        return rows('SELECT COUNT(*) fact_rows, COUNT(DISTINCT sales_detail_key) unique_details, COUNT(DISTINCT sales_order_id) orders, SUM(order_qty) units, SUM(line_total) revenue, COUNT(DISTINCT c.customer_id) active_customers FROM fact_online_sales f JOIN dim_customer c ON f.customer_key=c.customer_key',db)[0]
    values = {name:metrics(db) for name,db in [('selected_dump',selected),('legacy_dump',legacy),('safe_ddl_loaded',target)]}
    assert values['selected_dump']==values['legacy_dump']==values['safe_ddl_loaded']
    calendar_sql = """SELECT MIN(tanggal) minimum,MAX(tanggal) maximum,COUNT(*) days,COUNT(DISTINCT tanggal) unique_dates,
DATEDIFF(MAX(tanggal),MIN(tanggal))+1-COUNT(DISTINCT tanggal) missing_days,
SUM(tanggal_key<>CAST(DATE_FORMAT(tanggal,'%Y%m%d') AS UNSIGNED) OR tahun<>YEAR(tanggal) OR semester<>IF(MONTH(tanggal)<=6,1,2) OR kuartal<>QUARTER(tanggal) OR bulan<>MONTH(tanggal) OR minggu_dalam_tahun<>WEEKOFYEAR(tanggal) OR tanggal_dalam_bulan<>DAY(tanggal) OR hari_dalam_minggu<>DAYOFWEEK(tanggal) OR is_akhir_pekan<>IF(DAYOFWEEK(tanggal) IN(1,7),1,0) OR nama_bulan<>ELT(MONTH(tanggal),'Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember') OR nama_hari<>ELT(DAYOFWEEK(tanggal),'Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu')) invalid_attributes
FROM dim_date WHERE tanggal_key<>-1"""
    calendars={name:rows(calendar_sql,db)[0] for name,db in [('selected_dump',selected),('safe_ddl_loaded',target)]}
    assert calendars['safe_ddl_loaded']['missing_days']=='0'
    assert calendars['safe_ddl_loaded']['invalid_attributes']=='0'
    orphans={fk['COLUMN_NAME']:rows(f"SELECT COUNT(*) n FROM fact_online_sales f LEFT JOIN {fk['REFERENCED_TABLE_NAME']} d ON f.{fk['COLUMN_NAME']}=d.{fk['REFERENCED_COLUMN_NAME']} WHERE d.{fk['REFERENCED_COLUMN_NAME']} IS NULL",target)[0]['n'] for fk in fks}
    assert set(orphans.values())=={'0'}
    months=rows("SELECT DATE_FORMAT(d.tanggal,'%Y-%m') month,COUNT(*) detail_rows,COUNT(DISTINCT sales_order_id) orders,SUM(order_qty) units,SUM(line_total) revenue FROM fact_online_sales f JOIN dim_date d ON f.tanggal_key=d.tanggal_key GROUP BY 1 ORDER BY 1",selected)
    selected_unknown = {t:rows(f'SELECT COUNT(*) n FROM `{t}` WHERE `{k}`=-1',selected)[0]['n'] for t,k in TABLES.items() if t!='fact_online_sales'}
    report = {'executed_at_utc':datetime.now(timezone.utc).isoformat(),'engine':info['version'],'scope':'Private MySQL datadir under .audit-temp; no operational database touched','source_sha256':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['sql/adventureworks_dw (2).sql','sql/dump_adventureworks_dw.sql']},'schemas':{'selected':selected,'legacy':legacy,'ddl':target},'metrics':values,'calendar':calendars,'source_unknown_members':selected_unknown,'ddl_unknown_members':unknown,'ddl_rerun':{'status':'LULUS','all_table_hashes_before':before,'all_table_hashes_after':after},'constraints':constraints,'rebuild':{'without_confirmation':'LULUS: rejected with 1644 and all row hashes unchanged','confirmed_isolated_schema':'LULUS: all tables removed then recreated'},'foreign_keys':fks,'orphan_rows':orphans,'indexes':indexes,'columns':schemas,'monthly':months,'formal_calendar_standard':'BELUM DAPAT DIUJI: official lecturer template unavailable'}
    evidence=ROOT/'bukti/database/final';evidence.mkdir(parents=True,exist_ok=True)
    (evidence/'database-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # A fresh diagram generated from INFORMATION_SCHEMA, never relabeled as DBeaver.
    positions={'dim_date':(20,70),'dim_product':(20,460),'dim_customer':(20,810),'fact_online_sales':(660,330),'dim_territory':(1300,70),'dim_promotion':(1300,350),'dim_currency':(1300,630),'dim_ship_method':(1300,910)}
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1900" height="1240" viewBox="0 0 1900 1240">','<rect width="1900" height="1240" fill="#f4f8fc"/>','<style>text{font-family:Arial,sans-serif;font-size:17px}.title{font-size:22px;font-weight:bold}.field{font-family:Consolas,monospace;font-size:16px}</style>','<text class="title" x="20" y="35">Kelompok 2 — Skema aktual dari INFORMATION_SCHEMA (MySQL, audit terisolasi)</text>']
    for fk in fks:
        x,y=positions[fk['REFERENCED_TABLE_NAME']];fx,fy=positions['fact_online_sales']; left=x<fx
        sx=x+570 if left else x; tx=fx if left else fx+570
        parts.append(f'<path d="M{sx},{y+70} L{tx},{fy+180}" stroke="#2489c7" stroke-width="2" fill="none"/><text x="{sx+(-15 if left else 8)}" y="{y+62}">1</text><text x="{tx+(8 if left else -18)}" y="{fy+170}">N</text>')
    for table,(x,y) in positions.items():
        fields=[c for c in schemas if c['TABLE_NAME']==table];height=55+len(fields)*25
        parts.append(f'<rect x="{x}" y="{y}" width="570" height="{height}" fill="white" stroke="#2489c7"/><rect x="{x}" y="{y}" width="570" height="38" fill="#ddecf7"/><text class="title" x="{x+12}" y="{y+27}">{table}</text>')
        for i,c in enumerate(fields):
            tag='PK ' if c['COLUMN_KEY']=='PRI' else ('FK ' if any(f['COLUMN_NAME']==c['COLUMN_NAME'] and table=='fact_online_sales' for f in fks) else '')
            label=tag+c['COLUMN_NAME']+' : '+c['COLUMN_TYPE']+(' NOT NULL' if c['IS_NULLABLE']=='NO' else '')
            parts.append(f'<text class="field" x="{x+12}" y="{y+62+i*25}">{html.escape(label)}</text>')
    parts.append('<text x="20" y="1215">Grain: satu SalesOrderDetailID. Gambar historis DBeaver/Star Schema V2 dipertahankan; diagram ini dihasilkan oleh verify_database.py.</text></svg>')
    (ROOT/'docs/erd-skema-aktual.svg').write_text('\n'.join(parts),encoding='utf-8')
    print(json.dumps({'status':'LULUS runtime database','schemas':report['schemas'],'metrics':values['selected_dump'],'calendar':calendars,'formal_standard':report['formal_calendar_standard']},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
