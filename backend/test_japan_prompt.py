import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.agent.graph import travel_agent_app

prompt = 'Tôi muốn đi khắp Nhật Bản trong vòng 7 ngày 6 đêm. Ngân sách cho chuyến đi này là 500 triệu bao gồm tiền chuyến bay cả đi lẫn về của 4 người. Chuyến đi này dành cho gia đình 4 người. Chúng tôi ở Thành Phố Hồ Chí Minh.'
res = travel_agent_app.invoke({'user_prompt': prompt})
req = res['extracted_requirements']
itin = res.get('final_itinerary', [])
cost = res.get('budget_analysis', {}).get('total_estimated_cost', 0)

print('Parsed requirements:', req)
assert 'Hồ Chí Minh' in req['origin'], f"Origin error: {req['origin']}"
assert 'Nhật Bản' in req['destination'] or 'Tokyo' in req['destination'], f"Destination error: {req['destination']}"
assert req['travelers'] == 4, f"Travelers error: {req['travelers']}"
assert req['budget'] == 500000000.0, f"Budget error: {req['budget']}"
assert req['duration'] == 7, f"Duration error: {req['duration']}"

print(f"Generated {len(itin)} days. Total cost: {cost:,.0f} VND (Budget: 500M VND)")
assert len(itin) == 7, f"Expected 7 days, got {len(itin)}"
assert cost <= 500000000.0, f"Cost exceeded budget: {cost}"

# Check time order for each day
for d in itin:
    items = d['items']
    times = [item['start_time'] for item in items if 'start_time' in item]
    print(f"Day {d['day_number']}: {len(items)} items. Times: {times}")
    for i in range(len(times)-1):
        t1 = int(times[i].split(':')[0])*60 + int(times[i].split(':')[1])
        t2 = int(times[i+1].split(':')[0])*60 + int(times[i+1].split(':')[1])
        assert t1 <= t2, f"Time inversion on Day {d['day_number']}: {times[i]} followed by {times[i+1]}"

print('>>> ALL ASSERTIONS FOR JAPAN 7D 500M 4P PASSED PERFECTLY!')
