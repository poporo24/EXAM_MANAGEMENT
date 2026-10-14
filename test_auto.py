import system.database as db
# Let's say we are Auto-Scheduling exam 343 (PROFED EL for BAELS 301)
print(db.get_full_auto_schedule(343, 60, sync_all=False))
