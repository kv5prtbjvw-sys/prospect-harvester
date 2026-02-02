#!/usr/bin/env python3
"""
GUIDELIGHT PROSPECT RECOMMENDATIONS ENGINE
Find grant opportunities aligned with: "Providing biblical hope and practical help to families experiencing disability"
Sectors: Churches, Missionaries, Local Communities, Children & Families
"""

import requests
import sqlite3
import json

# Guidelight's mission keywords
GUIDELIGHT_KEYWORDS = [
      'disability', 'disabled', 'biblical', 'hope', 'families', 'children',
      'special needs', 'church', 'faith', 'ministry', 'community', 'practical help',
      'Christian', 'gospel', 'support', 'families with disabilities'
]

# Guidelight target sectors (NTEE codes)
TARGET_SECTORS = {
      'X': 'Churches & Religious Organizations',  # X20-X80
      'J': 'Disability Services',                  # JD
      'B': 'Children & Family Services',          # BF-BI
}

def score_nonprofit(org_data):
      """
          Score a nonprofit for alignment with Guidelight's mission
              Returns: 0-100 score
                  """
      score = 0

    # Check mission text
      mission_text = (org_data.get('mission') or '') + (org_data.get('name') or '')
      mission_lower = mission_text.lower()

    # Count keyword matches
      keyword_matches = sum(1 for kw in GUIDELIGHT_KEYWORDS if kw in mission_lower)
      score += keyword_matches * 5

    # Bonus for sector match
      ntee = org_data.get('ntee_code', '')
      if ntee and ntee[0] in TARGET_SECTORS:
                score += 20

      # Bonus for capacity
      capacity = org_data.get('capacity_rating', 0)
      score += capacity * 10

    # Cap at 100
      return min(score, 100)

def get_recommendations(limit=20):
      """
          Query database and return top nonprofit matches for Guidelight
              """
      try:
                conn = sqlite3.connect('backend/backend/nonprofits.db')
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

        # Get all organizations
                cursor.execute("SELECT * FROM organizations")
                orgs = [dict(row) for row in cursor.fetchall()]
                conn.close()

        if not orgs:
                      print("No organizations in database. Download data first with:")
                      print("python3 backend/backend/scripts/download_990.py")
                      return []

        # Score each org
        for org in orgs:
                      org['guidelight_score'] = score_nonprofit(org)

        # Sort by score
        orgs.sort(key=lambda x: x['guidelight_score'], reverse=True)

        return orgs[:limit]

except Exception as e:
        print(f"Error: {e}")
        return []

def display_recommendations(recommendations):
      """Pretty print recommendations"""
    print("\n" + "="*80)
    print("🎯 GUIDELIGHT PROSPECT RECOMMENDATIONS")
    print("Mission: Providing biblical hope and practical help to families experiencing disability")
    print("="*80)

    if not recommendations:
              print("\n✗ No organizations found. Database may be empty.")
              return

    print(f"\nFound {len(recommendations)} matching organizations\n")

    for i, org in enumerate(recommendations[:20], 1):
              score = org.get('guidelight_score', 0)

        # Color code by score
              if score >= 80:
                            rating = "⭐⭐⭐ EXCELLENT"
elif score >= 60:
            rating = "⭐⭐ GOOD"
elif score >= 40:
            rating = "⭐ FAIR"
else:
            rating = "OK"

        print(f"{i}. {org['name']}")
        print(f"   Location: {org['city']}, {org['state']}")
        print(f"   Match Score: {score:.0f}/100 {rating}")
        print(f"   Revenue: ${org.get('total_revenue', 0):,.0f}")
        print(f"   EIN: {org.get('ein')}")
        if org.get('website'):
                      print(f"   Website: {org['website']}")
                  print()

if __name__ == "__main__":
      print("\n🔍 Fetching Guidelight prospects...\n")
    recs = get_recommendations(limit=50)
    display_recommendations(recs)

    print("\n" + "="*80)
    print("💡 TIP: To download real IRS 990 data:")
    print("   python3 backend/backend/scripts/download_990.py")
    print("="*80 + "\n")
