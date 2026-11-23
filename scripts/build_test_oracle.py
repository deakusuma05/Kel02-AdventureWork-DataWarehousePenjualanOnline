"""Create independent SQL expectations from the isolated audit DW, never from UI totals."""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mysql', default=os.environ.get('MYSQL_CLIENT', 'mysql'))
    parser.add_argument('--port', type=int, default=13307)
    parser.add_argument('--database', default='adventureworks_dw')
    args = parser.parse_args()
    if args.port == 3306 or not args.database.replace('_', '').isalnum():
        raise SystemExit('Use the isolated audit database only')

    def query(sql):
        result = subprocess.run([args.mysql, '--protocol=TCP', '-h127.0.0.1', f'-P{args.port}', '-uroot', '--batch', '--raw', '--skip-column-names', args.database, '-e', sql], capture_output=True, text=True, encoding='utf-8', check=True)
        return [line.split('\t') for line in result.stdout.splitlines()]

    joins = '''FROM fact_online_sales f
        JOIN dim_tanggal d ON d.tanggal_key=f.tanggal_key
        JOIN dim_product p ON p.product_key=f.product_key
        JOIN dim_customer c ON c.customer_key=f.customer_key
        JOIN dim_territory t ON t.territory_key=f.territory_key
        JOIN dim_promotion pr ON pr.promotion_key=f.promotion_key
        JOIN dim_currency r ON r.currency_key=f.currency_key
        JOIN dim_ship_method s ON s.ship_method_key=f.ship_method_key'''
    years = [row[0] for row in query(f'SELECT DISTINCT d.tahun {joins} ORDER BY d.tahun')]
    regions = [row[0] for row in query(f'SELECT DISTINCT t.territory_name {joins} ORDER BY t.territory_name')]
    categories = [row[0] for row in query(f'SELECT DISTINCT p.category_name {joins} ORDER BY p.category_name')]
    scenarios = [{'name': 'all', 'year': '', 'region': '', 'category': ''}]
    for key, values in [('year', years), ('region', regions), ('category', categories)]:
        scenarios += [dict(name=f'{key}:{value}', year='', region='', category='', **{key: value}) for value in []]
        for value in values:
            scenario = dict(name=f'{key}:{value}', year='', region='', category='')
            scenario[key] = value
            scenarios.append(scenario)
    scenarios += [dict(name='combined', year=years[-1], region=regions[0], category=categories[-1]),
                  dict(name='empty', year=years[0], region=regions[0], category='Accessories')]
    columns = {'year': 'd.tahun', 'region': 't.territory_name', 'category': 'p.category_name'}
    for scenario in scenarios:
        # Values originate in this database; quote exact values and never accept query text.
        conditions = [columns[k] + "='" + scenario[k].replace('\\', '\\\\').replace("'", "''") + "'" for k in columns if scenario[k]]
        where = ' WHERE ' + ' AND '.join(conditions) if conditions else ''
        base = joins + where
        row = query(f'''SELECT COUNT(*), COUNT(DISTINCT f.sales_order_id), COALESCE(SUM(f.order_qty),0),
            COUNT(DISTINCT CASE WHEN c.customer_id <> -1 THEN c.customer_id END),
            CAST(COALESCE(SUM(f.line_total)*10000,0) AS SIGNED),
            COUNT(DISTINCT DATE_FORMAT(d.tanggal,'%Y-%m')),
            COUNT(DISTINCT CASE WHEN r.currency_rate_id=-1 THEN f.sales_order_id END) {base}''')[0]
        scenario['metrics'] = dict(zip(['details','orders','units','active_customers','revenue_scaled','months','orders_without_rate'], map(int,row)))
        scenario['months'] = [[r[0], int(r[1])] for r in query(f"SELECT DATE_FORMAT(d.tanggal,'%Y-%m'),CAST(SUM(f.line_total)*10000 AS SIGNED) {base} GROUP BY 1 ORDER BY 1")]
        scenario['products'] = [[int(r[0]),r[1],int(r[2])] for r in query(f'SELECT p.product_id, MIN(p.product_name), CAST(SUM(f.line_total)*10000 AS SIGNED) {base} GROUP BY p.product_id ORDER BY 3 DESC,1 LIMIT 10')]
        scenario['shipping'] = [[r[0],int(r[1])] for r in query(f'SELECT s.ship_method_name,COUNT(DISTINCT f.sales_order_id) {base} GROUP BY 1 ORDER BY 2 DESC,1')]
        scenario['currencies'] = [[r[0],int(r[1]),int(r[2])] for r in query(f"SELECT CASE WHEN r.currency_rate_id=-1 THEN 'Tanpa referensi kurs' ELSE r.to_currency_code END,COUNT(DISTINCT f.sales_order_id),CAST(SUM(f.line_total)*10000 AS SIGNED) {base} GROUP BY 1 ORDER BY 2 DESC,1")]
    output = ROOT/'bukti/audit-final/sql-dashboard-oracle.json'
    output.write_text(json.dumps({'source':'Actual MySQL isolated DW SQL queries','database':args.database,'scenarios':scenarios},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(scenarios)} SQL filter scenarios -> {output.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
