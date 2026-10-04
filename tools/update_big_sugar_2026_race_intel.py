#!/usr/bin/env python3
"""Correct 2026 Big Sugar race intel in seven delivered guide HTML files.

This touches the nonprotected plan brief and equipment sections only. The
existing race-week and race-day sections must remain byte-for-byte identical.
Organizer source: https://www.bigsugarclassic.com/gravel/ (2026 edition).
"""

from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES = sorted((ROOT / "athletes").glob("big-sugar-*/index.html"))
assert len(GUIDES) == 7, len(GUIDES)

RACE_CARD = """  <div class="data-card" style="margin-top: 16px;">
    <div class="data-card__header">2026 BIG SUGAR ROUTE &amp; CHECKPOINT PLAN</div>
    <div class="data-card__content">
      <p>The named 100 Mile Course is <strong>105.2 miles with about 6,700 feet of climbing</strong>. Expect loose, rocky Ozark gravel, some pavement and water crossings. Use the current organizer route and rules for final decisions; do not plan for a route that is just under 100 miles.</p>
      <ul>
        <li><strong>Start to Pineville:</strong> approximately 40 miles. The checkpoint cutoff is <strong>12:00 p.m.</strong> Practice a moving pace and stop budget that reaches it with a margin.</li>
        <li><strong>Pineville to Rockford Grange:</strong> approximately 38 more miles. The mile-78 checkpoint cutoff is <strong>4:00 p.m.</strong> Refill deliberately and leave time for rough roads, mechanical delays and the final 27.2 miles.</li>
        <li><strong>Carry and support:</strong> start with capacity for at least <strong>2 liters of water or sports drink</strong>; two ordinary bottles may be too small. Carry the required repair and navigation kit. <strong>There are no drop bags.</strong> Support crews may help at Pineville and Rockford Grange, not elsewhere on course.</li>
      </ul>
      <p>During a long-ride rehearsal, test your actual two-liter setup, nutrition access, rough-road handling, moving pace and realistic stop time. The organizer bases checkpoint cutoffs on 10 mph; treat that as a minimum planning constraint, not a recommended effort target. Recheck <a href="https://www.bigsugarclassic.com/gravel/">Life Time's course, aid-station details and rules</a> before travel.</p>
    </div>
  </div>

"""

EQUIPMENT_ITEMS = """    <li><strong>Mandatory fluid capacity:</strong> carry at least 2 liters of water or sports drink at the start; test the filled setup on rough gravel before race week.</li>
    <li><strong>Organizer-required kit:</strong> cycling computer or GPS, two spare inner tubes, inflation system, phone and helmet. Keep your existing repair kit accessible.</li>
    <li><strong>Handlebars:</strong> aerobars, bar extensions and clip-on attachments are prohibited.</li>
    <li><strong>Support:</strong> no drop bags; crew access is limited to the official Pineville and Rockford Grange checkpoints.</li>
"""

RACE_DAY_CARD_END = """      <p><strong>Saturday, October 17, 2026</strong></p>
    </div>
  </div>

"""
EQUIPMENT_ANCHOR = """    <li><strong>Lights:</strong> If there's any chance of finishing after dark</li>
"""


def protected_sections(value):
    return value[value.index('<section id="section-11"'):value.index('<section id="section-13"')]


for path in GUIDES:
    before = path.read_text()
    assert before.count(RACE_DAY_CARD_END) == 1, path
    assert before.count(EQUIPMENT_ANCHOR) == 1, path
    assert "2026 BIG SUGAR ROUTE &amp; CHECKPOINT PLAN" not in before, path
    protected_hash = sha256(protected_sections(before).encode()).hexdigest()
    after = before.replace(RACE_DAY_CARD_END, RACE_DAY_CARD_END + RACE_CARD, 1)
    after = after.replace(EQUIPMENT_ANCHOR, EQUIPMENT_ANCHOR + EQUIPMENT_ITEMS, 1)
    assert sha256(protected_sections(after).encode()).hexdigest() == protected_hash, path
    assert after.count("2026 BIG SUGAR ROUTE &amp; CHECKPOINT PLAN") == 1, path
    assert after.count("Mandatory fluid capacity:") == 1, path
    path.write_text(after)
    print(path.relative_to(ROOT), sha256(before.encode()).hexdigest(), sha256(after.encode()).hexdigest(), protected_hash)
