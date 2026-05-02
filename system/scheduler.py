"""
CCA Conflict-Free Exam Scheduler — v3
Assigns date + time + room + instructor automatically.

Constraints enforced:
  1. Time window: 07:00 – 20:00 daily
  2. No room double-booking (overlap-aware)
  3. No instructor double-booking (overlap-aware)
  4. Proctor availability (if set; defaults to all days)
  5. Max 2 Major exams per section per day
  6. Exams spread across the given 5–6 day period
  7. [NEW] Same subject_name → SAME date + time across all sections
         (anti-cheating: every section sits the exam simultaneously)
"""

from datetime import datetime, timedelta, date, time as dt_time
from collections import defaultdict

SLOT_INTERVAL_MIN = 60          # advance start time by 1 hour per slot
DAY_START = dt_time(7, 0)       # 07:00
DAY_END   = dt_time(20, 0)      # 20:00  (last exam must END by 20:00)


def _generate_slots(duration_minutes: int):
    """Return list of valid start dt_time values for the given duration."""
    slots = []
    from datetime import datetime as _dt
    end_limit = _dt(2000, 1, 1, 20, 0) - timedelta(minutes=duration_minutes)
    cur = _dt(2000, 1, 1, 7, 0)
    while cur <= end_limit:
        slots.append(cur.time())
        cur += timedelta(minutes=SLOT_INTERVAL_MIN)
    return slots


def _overlaps(s1, e1, s2, e2):
    return s1 < e2 and s2 < e1


def run_scheduler(pending_exams, rooms, instructors, booked_slots,
                  period_start: date, period_end: date,
                  proctor_availability: dict):
    """
    Parameters
    ----------
    pending_exams : list[dict]
        Keys: id, subject_name, section, subject_type, duration_minutes
    rooms : list[dict]
        Keys: id, room_name, capacity
    instructors : list[dict]
        Keys: id, name
    booked_slots : list[dict]
        Already-scheduled exams: room_id, instructor_id, exam_date_time,
        duration_minutes, section, subject_type
    period_start / period_end : date
        The 5-6 day exam window.
    proctor_availability : dict
        {instructor_id: set[date]}  — empty set means available all days.

    Returns
    -------
    dict with keys 'scheduled' (list) and 'failed' (list)
    """

    # ── Build existing calendars ─────────────────────────────────────────────
    room_cal  = defaultdict(list)   # room_id  -> [(start_dt, end_dt)]
    inst_cal  = defaultdict(list)   # inst_id  -> [(start_dt, end_dt)]
    # major-per-section-per-day counter  {section: {date: count}}
    maj_count = defaultdict(lambda: defaultdict(int))
    # Track slots already locked for a subject  {subject_name: start_dt}
    subject_locked_slot = {}

    for slot in booked_slots:
        r_id  = slot.get('room_id')
        i_id  = slot.get('instructor_id')
        dt    = slot.get('exam_date_time')
        dur   = slot.get('duration_minutes', 60)
        sec   = slot.get('section') or ''
        stype = slot.get('subject_type', 'Major')
        subj  = (slot.get('subject_name') or '').strip().lower()
        if dt and r_id:
            end = dt + timedelta(minutes=dur)
            room_cal[r_id].append((dt, end))
        if dt and i_id:
            end = dt + timedelta(minutes=dur)
            inst_cal[i_id].append((dt, end))
        if dt and stype == 'Major' and sec:
            maj_count[sec][dt.date()] += 1
        # Remember any already-scheduled slot for this subject
        if dt and subj and subj not in subject_locked_slot:
            subject_locked_slot[subj] = dt

    # ── Generate exam dates ──────────────────────────────────────────────────
    exam_dates = []
    cur = period_start
    while cur <= period_end:
        exam_dates.append(cur)
        cur += timedelta(days=1)

    # ── Group exams by subject_name (same subject → same slot) ───────────────
    # Each group is a list of exam dicts that share the same subject name.
    from collections import OrderedDict
    subject_groups = OrderedDict()
    for exam in pending_exams:
        key = (exam.get('subject_name') or '').strip().lower()
        subject_groups.setdefault(key, []).append(exam)

    # Sort groups: Major-only groups first (harder to place), then mixed/minor
    def group_sort_key(group):
        exams = group[1]
        has_major = any((e.get('subject_type') or 'Major') == 'Major' for e in exams)
        return (0 if has_major else 1, group[0])

    sorted_groups = sorted(subject_groups.items(), key=group_sort_key)

    # ── Helper predicates ────────────────────────────────────────────────────
    def room_free(r_id, s, e):
        return all(not _overlaps(s, e, a, b) for a, b in room_cal[r_id])

    def inst_free(i_id, s, e):
        return all(not _overlaps(s, e, a, b) for a, b in inst_cal[i_id])

    def inst_available(i_id, d):
        avail = proctor_availability.get(i_id)
        if not avail:           # no restrictions → always available
            return True
        return d in avail

    def section_major_ok(section, ex_date, is_major):
        if not is_major or not section:
            return True
        return maj_count[section][ex_date] < 2

    # ── Schedule group by group ──────────────────────────────────────────────
    scheduled = []
    failed    = []

    for subj_key, group_exams in sorted_groups:
        # All exams in this group share the same duration (use max to be safe)
        dur = max((e.get('duration_minutes') or 60) for e in group_exams)
        slots = _generate_slots(dur)
        n_needed = len(group_exams)     # rooms + proctors needed simultaneously

        # If this subject was already partially scheduled (booked_slots),
        # lock all new sections to that same slot.
        locked_start = subject_locked_slot.get(subj_key)

        placed_group = False

        candidate_datetimes = []
        if locked_start:
            # Must use the already-locked slot
            candidate_datetimes = [locked_start]
        else:
            # Try every date × time combination
            for ex_date in exam_dates:
                for slot_time in slots:
                    candidate_datetimes.append(datetime.combine(ex_date, slot_time))

        for start_dt in candidate_datetimes:
            end_dt   = start_dt + timedelta(minutes=dur)
            ex_date  = start_dt.date()

            # Check section major-cap for every exam in the group
            all_caps_ok = all(
                section_major_ok(
                    e.get('section') or '',
                    ex_date,
                    (e.get('subject_type') or 'Major') == 'Major'
                )
                for e in group_exams
            )
            if not all_caps_ok:
                continue

            # Find enough free rooms for every section simultaneously
            free_rooms = [r for r in rooms if room_free(r['id'], start_dt, end_dt)]
            if len(free_rooms) < n_needed:
                continue

            # Find enough free + available instructors
            free_insts = [
                i for i in instructors
                if inst_free(i['id'], start_dt, end_dt)
                and inst_available(i['id'], ex_date)
            ]
            if len(free_insts) < n_needed:
                continue

            # ── Assign all exams in the group to this slot ───────────────
            for idx, exam in enumerate(group_exams):
                section  = exam.get('section') or ''
                is_major = (exam.get('subject_type') or 'Major') == 'Major'

                scheduled.append({
                    'exam_id':         exam['id'],
                    'room_id':         free_rooms[idx]['id'],
                    'instructor_id':   free_insts[idx]['id'],
                    'instructor_name': free_insts[idx]['name'],
                    'exam_date_time':  start_dt,
                })
                room_cal[free_rooms[idx]['id']].append((start_dt, end_dt))
                inst_cal[free_insts[idx]['id']].append((start_dt, end_dt))
                if is_major and section:
                    maj_count[section][ex_date] += 1

            # Lock this slot for the subject so any future partial re-runs
            # also respect the same date/time.
            subject_locked_slot[subj_key] = start_dt
            placed_group = True
            break   # slot found — move to next subject group

        if not placed_group:
            for exam in group_exams:
                section  = exam.get('section') or ''
                is_major = (exam.get('subject_type') or 'Major') == 'Major'
                failed.append({
                    'exam_id': exam['id'],
                    'reason': (
                        f'No available slot where ALL {n_needed} section(s) of '
                        f'"{exam.get("subject_name", "")}" can sit simultaneously '
                        f'across the {len(exam_dates)}-day period '
                        f'({"major" if is_major else "minor"}, section: {section or "—"})'
                    )
                })

    return {'scheduled': scheduled, 'failed': failed}
