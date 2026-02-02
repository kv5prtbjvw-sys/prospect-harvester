#!/usr/bin/env python3
"""
Prospect Harvester - Project File Setup Script
This script creates all necessary project files with complete code.
Run this after cloning: python setup_files.py
"""

import os
import json
from pathlib import Path

def create_file(filepath, content):
      """Create a file with the given content"""
      path = Path(filepath)
      path.parent.mkdir(parents=True, exist_ok=True)
      with open(path, 'w') as f:
                f.write(content)
            print(f"✓ Created {filepath}")

# Backend app.py
app_py = '''from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = os.getenv('DATABASE_URL', 'nonprofits.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
            return conn

            def dict_from_row(row):
                return dict(row) if row else None

                @app.route('/api/search', methods=['GET'])
                def search_organizations():
                    query = request.args.get('q', '').strip()
                        sector = request.args.get('sector', '')
                            limit = request.args.get('limit', 100, type=int)

                                    conn = get_db()
                                        cursor = conn.cursor()

                                                sql = "SELECT * FROM organizations WHERE 1=1"
                                                    params = []

                                                            if query:
                                                                    sql += " AND (name LIKE ? OR ein LIKE ?)"
                                                                            params.extend([f"%{query}%", f"%{query}%"])

                                                                                    if sector == 'church':
                                                                                            sql += " AND ntee_code LIKE 'X%'"
                                                                                                elif sector == 'disability':
                                                                                                        sql += " AND ntee_code LIKE 'J%'"
                                                                                                            elif sector == 'children_families':
                                                                                                                    sql += " AND ntee_code LIKE 'B%'"
                                                                                                                        
                                                                                                                            sql += " ORDER BY alignment_score DESC, capacity_rating DESC LIMIT ?"
                                                                                                                                params.append(limit)
                                                                                                                                    
                                                                                                                                        cursor.execute(sql, params)
                                                                                                                                            results = [dict(row) for row in cursor.fetchall()]
                                                                                                                                                conn.close()
                                                                                                                                                    
                                                                                                                                                        return jsonify({'count': len(results), 'results': results})
                                                                                                                                                        
                                                                                                                                                        @app.route('/api/org/<int:org_id>', methods=['GET'])
                                                                                                                                                        def get_organization(org_id):
                                                                                                                                                            conn = get_db()
                                                                                                                                                                cursor = conn.cursor()
                                                                                                                                                                    
                                                                                                                                                                        cursor.execute("SELECT * FROM organizations WHERE id = ?", (org_id,))
                                                                                                                                                                            org = dict_from_row(cursor.fetchone())
                                                                                                                                                                                
                                                                                                                                                                                    if not org:
                                                                                                                                                                                            conn.close()
                                                                                                                                                                                                    return jsonify({'error': 'Not found'}), 404
                                                                                                                                                                                                        
                                                                                                                                                                                                            cursor.execute("SELECT * FROM board_members WHERE org_id = ?", (org_id,))
                                                                                                                                                                                                                board = [dict(row) for row in cursor.fetchall()]
                                                                                                                                                                                                                    
                                                                                                                                                                                                                        cursor.execute("SELECT * FROM financial_history WHERE org_id = ? ORDER BY tax_year DESC LIMIT 5", (org_id,))
                                                                                                                                                                                                                            financials = [dict(row) for row in cursor.fetchall()]
                                                                                                                                                                                                                                
                                                                                                                                                                                                                                    conn.close()
                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                            return jsonify({'organization': org, 'board_members': board, 'financial_history': financials})
                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                            @app.route('/api/lists', methods=['GET'])
                                                                                                                                                                                                                                            def get_lists():
                                                                                                                                                                                                                                                conn = get_db()
                                                                                                                                                                                                                                                    cursor = conn.cursor()
                                                                                                                                                                                                                                                        cursor.execute("SELECT * FROM prospect_lists ORDER BY created_date DESC")
                                                                                                                                                                                                                                                            lists = [dict(row) for row in cursor.fetchall()]
                                                                                                                                                                                                                                                                conn.close()
                                                                                                                                                                                                                                                                    return jsonify(lists)
                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                    @app.route('/api/lists', methods=['POST'])
                                                                                                                                                                                                                                                                    def create_list():
                                                                                                                                                                                                                                                                        data = request.json
                                                                                                                                                                                                                                                                            if not data.get('name'):
                                                                                                                                                                                                                                                                                    return jsonify({'error': 'Name required'}), 400
                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                            conn = get_db()
                                                                                                                                                                                                                                                                                                cursor = conn.cursor()
                                                                                                                                                                                                                                                                                                    cursor.execute("INSERT INTO prospect_lists (name, description, goal_amount, criteria_json, created_date, modified_date) VALUES (?, ?, ?, ?, ?, ?)",
                                                                                                                                                                                                                                                                                                                       (data['name'], data.get('description', ''), data.get('goal_amount', 0), json.dumps(data.get('criteria', {})), datetime.now(), datetime.now()))
                                                                                                                                                                                                                                                                                                                           conn.commit()
                                                                                                                                                                                                                                                                                                                               list_id = cursor.lastrowid
                                                                                                                                                                                                                                                                                                                                   conn.close()
                                                                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                                           return jsonify({'id': list_id}), 201
                                                                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                                                           @app.route('/api/stats', methods=['GET'])
                                                                                                                                                                                                                                                                                                                                           def get_stats():
                                                                                                                                                                                                                                                                                                                                               conn = get_db()
                                                                                                                                                                                                                                                                                                                                                   cursor = conn.cursor()
                                                                                                                                                                                                                                                                                                                                                       cursor.execute("SELECT COUNT(*) as count FROM organizations")
                                                                                                                                                                                                                                                                                                                                                           total_orgs = dict(cursor.fetchone())['count']
                                                                                                                                                                                                                                                                                                                                                               cursor.execute("SELECT COUNT(*) as count FROM prospect_lists")
                                                                                                                                                                                                                                                                                                                                                                   total_lists = dict(cursor.fetchone())['count']
                                                                                                                                                                                                                                                                                                                                                                       conn.close()
                                                                                                                                                                                                                                                                                                                                                                           return jsonify({'total_organizations': total_orgs, 'total_lists': total_lists})
                                                                                                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                                                                                           @app.route('/api/health', methods=['GET'])
                                                                                                                                                                                                                                                                                                                                                                           def health_check():
                                                                                                                                                                                                                                                                                                                                                                               return jsonify({'status': 'ok'})
                                                                                                                                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                                                                                               if __name__ == '__main__':
                                                                                                                                                                                                                                                                                                                                                                                   app.run(debug=True, port=5000)
                                                                                                                                                                                                                                                                                                                                                                                   '''

# Backend init_db.py
init_db_py = '''import sqlite3
import os

DB_PATH = os.getenv('DATABASE_URL', 'nonprofits.db')

def init_database():
    conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

                print("Creating database tables...")

                        cursor.execute("""CREATE TABLE IF NOT EXISTS organizations (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        ein TEXT UNIQUE NOT NULL, name TEXT NOT NULL, state TEXT, city TEXT, zip TEXT,
                                                mission TEXT, website TEXT, ntee_code TEXT, total_revenue DECIMAL, total_expenses DECIMAL,
                                                        net_assets DECIMAL, alignment_score INTEGER DEFAULT 0, capacity_rating INTEGER DEFAULT 0,
                                                                last_990_year INTEGER, last_updated TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                                                    )""")

                                                                            cursor.execute("""CREATE TABLE IF NOT EXISTS board_members (
                                                                                    id INTEGER PRIMARY KEY AUTOINCREMENT, org_id INTEGER NOT NULL, name TEXT NOT NULL,
                                                                                            title TEXT, compensation DECIMAL, FOREIGN KEY(org_id) REFERENCES organizations(id)
                                                                                                )""")
                                                                                                    
                                                                                                        cursor.execute("""CREATE TABLE IF NOT EXISTS financial_history (
                                                                                                                id INTEGER PRIMARY KEY AUTOINCREMENT, org_id INTEGER NOT NULL, tax_year INTEGER NOT NULL,
                                                                                                                        total_revenue DECIMAL, total_expenses DECIMAL, net_assets DECIMAL,
                                                                                                                                FOREIGN KEY(org_id) REFERENCES organizations(id)
                                                                                                                                    )""")
                                                                                                                                        
                                                                                                                                            cursor.execute("""CREATE TABLE IF NOT EXISTS prospect_lists (
                                                                                                                                                    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT,
                                                                                                                                                            goal_amount DECIMAL, criteria_json TEXT, created_date TIMESTAMP, modified_date TIMESTAMP
                                                                                                                                                                )""")
                                                                                                                                                                    
                                                                                                                                                                        cursor.execute("""CREATE TABLE IF NOT EXISTS list_members (
                                                                                                                                                                                id INTEGER PRIMARY KEY AUTOINCREMENT, list_id INTEGER NOT NULL, org_id INTEGER NOT NULL,
                                                                                                                                                                                        notes TEXT, added_date TIMESTAMP, FOREIGN KEY(list_id) REFERENCES prospect_lists(id),
                                                                                                                                                                                                FOREIGN KEY(org_id) REFERENCES organizations(id), UNIQUE(list_id, org_id)
                                                                                                                                                                                                    )""")
                                                                                                                                                                                                        
                                                                                                                                                                                                            cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_ein ON organizations(ein)")
                                                                                                                                                                                                                cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_state ON organizations(state)")
                                                                                                                                                                                                                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_ntee ON organizations(ntee_code)")
                                                                                                                                                                                                                        cursor.execute("CREATE INDEX IF NOT EXISTS idx_org_alignment ON organizations(alignment_score)")
                                                                                                                                                                                                                            
                                                                                                                                                                                                                                conn.commit()
                                                                                                                                                                                                                                    conn.close()
                                                                                                                                                                                                                                        print(f"✓ Database initialized at {DB_PATH}")
                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                        if __name__ == '__main__':
                                                                                                                                                                                                                                            init_database()
                                                                                                                                                                                                                                            '''

# Backend download_990.py
download_990_py = '''import requests, zipfile, shutil
from pathlib import Path

def download_990_data(year=2024):
    base_url = f"https://apps.irs.gov/pub/epostcard/990/xml/{year}"
        data_dir = Path("990_data")
            data_dir.mkdir(exist_ok=True)
                extract_dir = Path("990_extracts")
                    if extract_dir.exists(): shutil.rmtree(extract_dir)
                        extract_dir.mkdir(exist_ok=True)

                                months = ['01A', '02A', '03A', '04A', '05A', '06A', '07A', '08A', '09A', '10A', '11A', '11B', '11C', '11D', '12A']
                                    print(f"Downloading IRS 990 data for {year}...")

                                            downloaded, failed = 0, 0
                                                for month in months:
                                                        filename = f"{year}_TEOS_XML_{month}.zip"
                                                                url = f"{base_url}/{filename}"
                                                                        filepath = data_dir / filename

                                                                                        try:
                                                                                                    print(f"Downloading {filename}...", end=' ')
                                                                                                                response = requests.get(url, timeout=30)
                                                                                                                            if response.status_code == 200:
                                                                                                                                            with open(filepath, 'wb') as f: f.write(response.content)
                                                                                                                                                            with zipfile.ZipFile(filepath, 'r') as z: z.extractall(extract_dir)
                                                                                                                                                                            print("✓")
                                                                                                                                                                                            downloaded += 1
                                                                                                                                                                                                        else:
                                                                                                                                                                                                                        print(f"✗ ({response.status_code})")
                                                                                                                                                                                                                                        failed += 1
                                                                                                                                                                                                                                                except Exception as e:
                                                                                                                                                                                                                                                            print(f"✗ ({str(e)})")
                                                                                                                                                                                                                                                                        failed += 1
                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                xml_files = list(extract_dir.glob("*.xml"))
                                                                                                                                                                                                                                                                                    print(f"\\n✓ Downloaded: {downloaded}, Failed: {failed}")
                                                                                                                                                                                                                                                                                        print(f"✓ Extracted {len(xml_files)} XML files")
                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                        if __name__ == '__main__':
                                                                                                                                                                                                                                                                                            download_990_data()
                                                                                                                                                                                                                                                                                            '''

# Backend parse_990.py
parse_990_py = '''import sqlite3, xmltodict
from pathlib import Path
from datetime import datetime

SECTOR_KEYWORDS = {
    'disability': ['disabled', 'disability', 'blind', 'deaf', 'wheelchair', 'special needs', 'autism'],
        'children_families': ['children', 'youth', 'family', 'child care', 'foster', 'adoption'],
            'church': ['church', 'christian', 'faith', 'gospel', 'ministry', 'evangelical', 'baptist']
            }

            def calculate_alignment_score(mission_text, ntee_code, org_name):
                text_lower = (mission_text or '' + org_name or '').lower()
                    score = 0
                        if any(kw in text_lower for kw in SECTOR_KEYWORDS['disability']): score += 2
                            if any(kw in text_lower for kw in SECTOR_KEYWORDS['children_families']): score += 2
                                if any(kw in text_lower for kw in SECTOR_KEYWORDS['church']): score += 2
                                    if ntee_code:
                                            if ntee_code.startswith('X'): score += 1
                                                    elif ntee_code.startswith('J'): score += 1
                                                            elif ntee_code.startswith('B'): score += 1
                                                                return min(score, 5)

                                                                def calculate_capacity_score(total_revenue):
                                                                    if not total_revenue: return 1
                                                                        revenue = float(total_revenue) if total_revenue else 0
                                                                            if revenue < 100000: return 1
                                                                                elif revenue < 500000: return 2
                                                                                    elif revenue < 2000000: return 3
                                                                                        elif revenue < 10000000: return 4
                                                                                            else: return 5

                                                                                            def parse_990_file(xml_file):
                                                                                                try:
                                                                                                        with open(xml_file, 'r', encoding='utf-8') as f: data = xmltodict.parse(f.read())
                                                                                                                return_data = data.get('Return', {})
                                                                                                                        header = return_data.get('ReturnHeader', {})
                                                                                                                                filer = header.get('Filer', {})
                                                                                                                                        org_data = {
                                                                                                                                                    'ein': filer.get('EIN'),
                                                                                                                                                                'name': filer.get('BusinessName', {}).get('BusinessNameLine1'),
                                                                                                                                                                            'state': filer.get('USAddress', {}).get('State'),
                                                                                                                                                                                        'city': filer.get('USAddress', {}).get('City'),
                                                                                                                                                                                                    'zip': filer.get('USAddress', {}).get('ZIPCode'),
                                                                                                                                                                                                                'website': filer.get('WebsiteAddress'),
                                                                                                                                                                                                                            'ntee_code': header.get('OrganizationInformation', {}).get('PrimaryNTEECode'),
                                                                                                                                                                                                                                        'tax_year': header.get('TaxYear'),
                                                                                                                                                                                                                                                }
                                                                                                                                                                                                                                                        irc990 = return_data.get('IRS990', {})
                                                                                                                                                                                                                                                                org_data['total_revenue'] = irc990.get('CYTotalRevenue') or 0
                                                                                                                                                                                                                                                                        org_data['total_expenses'] = irc990.get('CYTotalExpenses') or 0
                                                                                                                                                                                                                                                                                org_data['net_assets'] = irc990.get('NetAssetsOrFundBalances') or 0
                                                                                                                                                                                                                                                                                        org_data['mission'] = irc990.get('ActivityDescription')
                                                                                                                                                                                                                                                                                                return org_data
                                                                                                                                                                                                                                                                                                    except: return None
                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                    def import_organizations(xml_dir='990_extracts'):
                                                                                                                                                                                                                                                                                                        conn = sqlite3.connect('nonprofits.db')
                                                                                                                                                                                                                                                                                                            cursor = conn.cursor()
                                                                                                                                                                                                                                                                                                                xml_files = list(Path(xml_dir).glob("*.xml"))
                                                                                                                                                                                                                                                                                                                    print(f"Processing {len(xml_files)} XML files...")
                                                                                                                                                                                                                                                                                                                        imported = 0
                                                                                                                                                                                                                                                                                                                            for i, xml_file in enumerate(xml_files):
                                                                                                                                                                                                                                                                                                                                    if (i + 1) % 100 == 0: print(f"  {i + 1}/{len(xml_files)}...")
                                                                                                                                                                                                                                                                                                                                            org_data = parse_990_file(xml_file)
                                                                                                                                                                                                                                                                                                                                                    if not org_data or not org_data.get('ein'): continue
                                                                                                                                                                                                                                                                                                                                                            try:
                                                                                                                                                                                                                                                                                                                                                                        alignment = calculate_alignment_score(org_data.get('mission', ''), org_data.get('ntee_code', ''), org_data.get('name', ''))
                                                                                                                                                                                                                                                                                                                                                                                    capacity = calculate_capacity_score(org_data.get('total_revenue'))
                                                                                                                                                                                                                                                                                                                                                                                                cursor.execute("INSERT OR REPLACE INTO organizations (ein,name,state,city,zip,mission,website,ntee_code,total_revenue,total_expenses,net_assets,alignment_score,capacity_rating,last_990_year,last_updated) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                                                                                                                                                                                                                                                                                                                                                                                                           (org_data['ein'], org_data['name'], org_data['state'], org_data['city'], org_data['zip'], org_data['mission'], org_data['website'], org_data['ntee_code'], org_data['total_revenue'], org_data['total_expenses'], org_data['net_assets'], alignment, capacity, org_data['tax_year'], datetime.now()))
                                                                                                                                                                                                                                                                                                                                                                                                                                       imported += 1
                                                                                                                                                                                                                                                                                                                                                                                                                                               except: pass
                                                                                                                                                                                                                                                                                                                                                                                                                                                   conn.commit()
                                                                                                                                                                                                                                                                                                                                                                                                                                                       conn.close()
                                                                                                                                                                                                                                                                                                                                                                                                                                                           print(f"\\n✓ Imported {imported} organizations")
                                                                                                                                                                                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                                                                                                                                                                           if __name__ == '__main__':
                                                                                                                                                                                                                                                                                                                                                                                                                                                               import_organizations()
                                                                                                                                                                                                                                                                                                                                                                                                                                                               '''

# Frontend package.json
package_json = {
      "name": "prospect-harvester-frontend",
      "version": "1.0.0",
      "private": True,
      "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "axios": "^1.4.0"
      },
      "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test"
      },
      "devDependencies": {
                "react-scripts": "5.0.1"
      }
}

# Frontend App.jsx
app_jsx = '''import React, { useState } from 'react';
import './App.css';

function App() {
    const [searchQuery, setSearchQuery] = useState('');
        const [sector, setSector] = useState('');
            const [results, setResults] = useState([]);
                const [loading, setLoading] = useState(false);

                    const handleSearch = async (e) => {
                            e.preventDefault();
                                    setLoading(true);
                                            try {
                                                        const response = await fetch(`http://localhost:5000/api/search?q=${searchQuery}&sector=${sector}`);
                                                                    const data = await response.json();
                                                                                setResults(data.results || []);
                                                                                        } catch (error) {
                                                                                                    console.error('Error:', error);
                                                                                                            }
                                                                                                                    setLoading(false);
                                                                                                                        };
                                                                                                                        
                                                                                                                            return (
                                                                                                                                    <div className="app">
                                                                                                                                                <nav className="navbar">
                                                                                                                                                                <h1>🎯 Prospect Harvester</h1>
                                                                                                                                                                            </nav>
                                                                                                                                                                                        <div className="container">
                                                                                                                                                                                                        <form onSubmit={handleSearch}>
                                                                                                                                                                                                                            <input type="text" placeholder="Search by name or EIN..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
                                                                                                                                                                                                                                                <select value={sector} onChange={(e) => setSector(e.target.value)}>
                                                                                                                                                                                                                                                                        <option value="">All Sectors</option>
                                                                                                                                                                                                                                                                                                <option value="church">Churches</option>
                                                                                                                                                                                                                                                                                                                        <option value="disability">Disability Services</option>
                                                                                                                                                                                                                                                                                                                                                <option value="children_families">Children & Families</option>
                                                                                                                                                                                                                                                                                                                                                                    </select>
                                                                                                                                                                                                                                                                                                                                                                                        <button type="submit">Search</button>
                                                                                                                                                                                                                                                                                                                                                                                                        </form>
                                                                                                                                                                                                                                                                                                                                                                                                                        {loading && <p>Loading...</p>}
                                                                                                                                                                                                                                                                                                                                                                                                                                        <div className="results">
                                                                                                                                                                                                                                                                                                                                                                                                                                                            {results.map(org => (
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    <div key={org.id} className="card">
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                <h2>{org.name}</h2>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            <p>{org.city}, {org.state}</p>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        <div className="metrics">
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        <div><span>Alignment</span><strong>{org.alignment_score}/5</strong></div>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        <div><span>Capacity</span><strong>{org.capacity_rating}/5</strong></div>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        <div><span>Revenue</span><strong>${(org.total_revenue/1000000).toFixed(1)}M</strong></div>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    </div>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            </div>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                ))}
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                </div>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            </div>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    </div>
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        );
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        }
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        export default App;
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        '''

# Frontend App.css
app_css = '''* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; }
.app { min-height: 100vh; }
.navbar { background: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.navbar h1 { color: #2563eb; font-size: 24px; }
.container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
form { display: flex; gap: 10px; margin-bottom: 30px; }
form input, form select { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
form button { padding: 12px 24px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer; }
form button:hover { background: #1d4ed8; }
.results { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.card h2 { margin-bottom: 8px; font-size: 18px; }
.card p { color: #666; margin-bottom: 16px; }
.metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.metrics div { text-align: center; padding: 12px; background: #f9fafb; border-radius: 4px; }
.metrics span { display: block; font-size: 12px; color: #666; margin-bottom: 4px; }
.metrics strong { display: block; font-size: 20px; color: #2563eb; }
p { text-align: center; color: #666; margin: 20px; }
'''

# Frontend index.js
index_js = '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<React.StrictMode><App /></React.StrictMode>);
'''

# Frontend index.html
index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Prospect Harvester</title>
            </head>
            <body>
                <div id="root"></div>
                </body>
                </html>
                '''

# .env.example
env_example = '''FLASK_ENV=development
DATABASE_URL=nonprofits.db
FLASK_DEBUG=1
'''

# .env
env_file = '''FLASK_ENV=development
DATABASE_URL=nonprofits.db
'''

# Requirements
requirements_txt = '''Flask==2.3.0
Flask-CORS==4.0.0
requests==2.31.0
lxml==4.9.2
xmltodict==0.13.0
python-dotenv==1.0.0
'''

# SETUP MAIN
print("=" * 50)
print("PROSPECT HARVESTER - FILE SETUP")
print("=" * 50)

# Create files
create_file('backend/app.py', app_py)
create_file('backend/init_db.py', init_db_py)
create_file('backend/scripts/download_990.py', download_990_py)
create_file('backend/scripts/parse_990.py', parse_990_py)
create_file('backend/requirements.txt', requirements_txt)
create_file('frontend/package.json', json.dumps(package_json, indent=2))
create_file('frontend/src/App.jsx', app_jsx)
create_file('frontend/src/App.css', app_css)
create_file('frontend/src/index.js', index_js)
create_file('frontend/public/index.html', index_html)
create_file('.env', env_file)
create_file('.env.example', env_example)

print("\n" + "=" * 50)
print("✓ ALL FILES CREATED SUCCESSFULLY!")
print("=" * 50)
print("\nNext steps:")
print("1. cd prospect-harvester")
print("2. git add .")
print("3. git commit -m 'Add complete app structure'")
print("4. git push origin main")
print("\nThen follow the README for running the app!")
