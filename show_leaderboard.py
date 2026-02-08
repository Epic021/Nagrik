import sys, json

data = json.load(sys.stdin)
print('=== DEPARTMENT LEADERBOARD ===')
print(f"{'Rank':<5} {'Department':<35} {'Total':<7} {'Resolved':<9} {'Rate':<8} {'Score':<6}")
print('-' * 75)
for i, d in enumerate(data['rankings'][:10], 1):
    print(f"{i:<5} {d['name'][:34]:<35} {d['total_complaints']:<7} {d['resolved']:<9} {d['resolution_rate']:<7}% {d['score']:<6}")
