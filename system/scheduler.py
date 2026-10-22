from datetime import datetime, timedelta, date, time as dt_time
from collections import defaultdict, OrderedDict

def _generate_slots(duration_minutes: int, day_start: dt_time, day_end: dt_time, interval: int):
    slots = []
    end_limit = datetime(2000, 1, 1, day_end.hour, day_end.minute) - timedelta(minutes=duration_minutes)
    cur = datetime(2000, 1, 1, day_start.hour, day_start.minute)
    while cur <= end_limit:
        slots.append(cur.time())
        cur += timedelta(minutes=interval)
    return slots

def _overlaps(s1, e1, s2, e2):
    return s1 < e2 and s2 < e1

def _to_time(val, default):
    from datetime import timedelta as _td, time as _time
    if isinstance(val, _td): return (datetime.min + val).time()
    if isinstance(val, _time): return val
    if isinstance(val, str):
        parts = val.split(':')
        if len(parts) >= 2: return _time(int(parts[0]), int(parts[1]))
    return default

def run_scheduler(pending_exams, rooms, instructors, booked_slots,
                  period_start: date, period_end: date, proctor_availability: dict,
                  settings=None):
    
    if settings is None: settings = {}
    day_start = _to_time(settings.get('day_start'), dt_time(7, 0))
    day_end = _to_time(settings.get('day_end'), dt_time(20, 0))
    slot_interval = int(settings.get('slot_interval_min', 60))
    max_consec_hrs = float(settings.get('max_consecutive_proctor_hrs') or settings.get('max_proctor_hrs') or 3.0)
    max_daily_hrs = float(settings.get('max_daily_proctor_hrs') or 4.0)
    travel_buffer = int(settings.get('travel_buffer_min', 15))

    room_cal = defaultdict(list)
    inst_cal = defaultdict(list)
    section_cal   = defaultdict(list)   # section -> [(start, end), ...]
    maj_count     = defaultdict(lambda: defaultdict(int))  # section -> date -> int
    min_count     = defaultdict(lambda: defaultdict(int))  # section -> date -> int (minor)
    total_exam_count = defaultdict(lambda: defaultdict(int))  # section -> date -> int (all types)
    subject_locked_slot = {}
    inst_last_building = defaultdict(dict)
    inst_consecutive_hours = defaultdict(lambda: defaultdict(list))
    inst_daily_hours = defaultdict(lambda: defaultdict(float))  # inst_id -> date -> total hours
    inst_total_hours = defaultdict(float)                       # inst_id -> cumulative hours across exam period
    inst_last_assigned = defaultdict(lambda: -1)                # inst_id -> assignment order for fair rotation
    assign_counter = [0]
    
    inst_map = {i['id']: i for i in instructors}
    room_map = {r['id']: r for r in rooms}

    for slot in booked_slots:
        r_id = slot.get('room_id')
        i_id = slot.get('instructor_id')
        dt = slot.get('exam_date_time')
        dur = slot.get('duration_minutes', 60)
        sec = slot.get('section') or ''
        stype = slot.get('subject_type', 'Major')
        subj = (slot.get('subject_name') or '').strip().lower()
        if dt and r_id:
            end = dt + timedelta(minutes=dur)
            room_cal[r_id].append((dt, end))
        if dt and i_id:
            end = dt + timedelta(minutes=dur)
            inst_cal[i_id].append((dt, end))
            # Track consec hours roughly for existing
            inst_consecutive_hours[i_id][dt.date()].append((dt, end))
            dur_hrs = dur / 60.0
            inst_daily_hours[i_id][dt.date()] += dur_hrs
            inst_total_hours[i_id] += dur_hrs
            inst_last_assigned[i_id] = assign_counter[0]
            assign_counter[0] += 1
            # Last building
            if r_id in room_map:
                inst_last_building[i_id][dt.date()] = (end, room_map[r_id].get('building'))
        if dt and sec:
            end = dt + timedelta(minutes=dur)
            section_cal[sec.strip()].append((dt, end))
        if dt and sec:
            ex_date = dt.date()
            if stype == 'Major':
                maj_count[sec][ex_date] += 1
            else:
                min_count[sec][ex_date] += 1
            total_exam_count[sec][ex_date] += 1
        # Build subject lock key using same priority as grouping
        cg_id  = slot.get('content_group_id')
        s_id   = slot.get('subject_id')
        subj   = (slot.get('subject_name') or '').strip().lower()
        if cg_id:
            lock_key = f"cg_{cg_id}"
        elif s_id:
            lock_key = f"sid_{s_id}"
        else:
            lock_key = subj
        if dt and lock_key and lock_key not in subject_locked_slot:
            subject_locked_slot[lock_key] = dt
        if dt and cg_id and s_id:
            sub_lock_key = f"cg_{cg_id}_s_{s_id}"
            if sub_lock_key not in subject_locked_slot:
                subject_locked_slot[sub_lock_key] = dt

    exam_dates = []
    cur = period_start
    while cur <= period_end:
        exam_dates.append(cur)
        cur += timedelta(days=1)

    # Group by: content_group_id (highest priority) → subject_id → subject_name
    # When subjects are linked into a content group:
    # - If all sections across linked subjects are disjoint (e.g. ENVISCI and GENDSOC),
    #   all sections are scheduled simultaneously in the exact same slot.
    # - If linked subjects share common sections (e.g. 6ADPROG and 6DATAS both taken by C101),
    #   students cannot take two exams at the same time. Partition by subject so every subject
    #   gets scheduled safely without dropping any exams!
    raw_cg_groups = OrderedDict()
    subject_groups = OrderedDict()
    for exam in pending_exams:
        cg_id = exam.get('content_group_id')
        subj_id = exam.get('subject_id')
        if cg_id:
            raw_cg_groups.setdefault(cg_id, []).append(exam)
        elif subj_id:
            key = f"sid_{subj_id}"
            subject_groups.setdefault(key, []).append(exam)
        else:
            key = (exam.get('subject_name') or '').strip().lower()
            subject_groups.setdefault(key, []).append(exam)

    for cg_id, exams_in_cg in raw_cg_groups.items():
        sec_list = [e.get('section').strip() for e in exams_in_cg if e.get('section') and e.get('section').strip()]
        if len(sec_list) == len(set(sec_list)):
            subject_groups[f"cg_{cg_id}"] = exams_in_cg
        else:
            # Overlapping sections inside this alias group:
            # Partition by subject_id so each individual subject is scheduled in its own slot
            by_subj = OrderedDict()
            for ex in exams_in_cg:
                sid = ex.get('subject_id') or (ex.get('subject_name') or '').strip().lower()
                by_subj.setdefault(sid, []).append(ex)
            for sid, sub_exams in by_subj.items():
                subject_groups[f"cg_{cg_id}_s_{sid}"] = sub_exams

    def group_sort_key(group):
        exams = group[1]
        has_major = any((e.get('subject_type') or 'Major') == 'Major' for e in exams)
        return (0 if has_major else 1, group[0])

    sorted_groups = sorted(subject_groups.items(), key=group_sort_key)

    def room_free(r_id, s, e):
        return all(not _overlaps(s, e, a, b) for a, b in room_cal[r_id])

    def inst_free(i_id, s, e):
        return all(not _overlaps(s, e, a, b) for a, b in inst_cal[i_id])

    def section_free(sec, s, e):
        """Return True if the section has no other exam overlapping [s, e) plus a 1-hour break."""
        if not sec or not sec.strip():
            return True  # no section assigned → no constraint
        s_buf = s - timedelta(hours=1)
        e_buf = e + timedelta(hours=1)
        return all(not (s_buf < b and a < e_buf) for a, b in section_cal[sec.strip()])

    def inst_available(i_id, exam_start_dt, exam_end_dt):
        avail_entries = proctor_availability.get(i_id)
        # If no availability has been set for this proctor, treat them as
        # fully available during the exam day (do NOT block them).
        if not avail_entries:
            return True
        exam_date = exam_start_dt.date()
        exam_start_time = exam_start_dt.time()
        exam_end_time = exam_end_dt.time()
        has_entry_for_date = False
        for entry in avail_entries:
            entry_date = entry['date']
            if isinstance(entry_date, datetime): entry_date = entry_date.date()
            if entry_date != exam_date: continue
            has_entry_for_date = True
            avail_start = _to_time(entry.get('start_time'), dt_time(7,0))
            avail_end = _to_time(entry.get('end_time'), dt_time(20,0))
            if exam_start_time >= avail_start and exam_end_time <= avail_end:
                return True
        # If entries exist but none match this date, treat as unavailable that day.
        # If no entry exists at all for this date, treat as available.
        return not has_entry_for_date
    
    def get_consecutive_hours(i_id, exam_date, s, e):
        blocks = inst_consecutive_hours[i_id][exam_date] + [(s, e)]
        blocks.sort(key=lambda x: x[0])
        total_mins = 0
        current_start = blocks[0][0]
        current_end = blocks[0][1]
        max_duration = 0
        for i in range(1, len(blocks)):
            if (blocks[i][0] - current_end).total_seconds() <= 15 * 60:
                current_end = max(current_end, blocks[i][1])
            else:
                max_duration = max(max_duration, (current_end - current_start).total_seconds())
                current_start = blocks[i][0]
                current_end = blocks[i][1]
        max_duration = max(max_duration, (current_end - current_start).total_seconds())
        return max_duration / 3600.0

    scheduled = []
    failed = []

    for subj_key, group_exams in sorted_groups:
        dur = max((e.get('duration_minutes') or 60) for e in group_exams)
        slots = _generate_slots(dur, day_start, day_end, slot_interval)
        n_needed = len(group_exams)

        locked_start = subject_locked_slot.get(subj_key)
        placed_group = False

        candidate_datetimes = []
        if locked_start:
            candidate_datetimes = [locked_start]
        else:
            for ex_date in exam_dates:
                for slot_time in slots:
                    candidate_datetimes.append(datetime.combine(ex_date, slot_time))
            
            # Spread exams evenly across the time frame.
            is_major_group = any((e.get('subject_type') or 'Major') == 'Major' for e in group_exams)
            
            def sort_key_for_date(dt):
                d = dt.date()
                max_total = 0
                max_majors = 0
                for e in group_exams:
                    sec = (e.get('section') or '').strip()
                    if sec:
                        max_total = max(max_total, total_exam_count[sec][d])
                        max_majors = max(max_majors, maj_count[sec][d])
                
                # If placing a Major, heavily penalize days that already have Majors to spread them out.
                # If placing a Minor, just focus on balancing the overall daily load.
                if is_major_group:
                    return (max_majors, max_total)
                else:
                    return (max_total, max_majors)
            
            candidate_datetimes.sort(key=sort_key_for_date)

        dur_hrs = dur / 60.0
        # Multi-tier relaxation: Try strict major limit and daily hour limit first.
        # If no slot is found satisfying the tight constraints, relax slightly so no exam is left unscheduled.
        limit_tiers = [
            (2, max_daily_hrs),
            (3, max_daily_hrs),
            (3, max_daily_hrs + 2.0),
            (3, max(max_daily_hrs + 4.0, 8.0))
        ]
        for major_limit, allowed_daily_hrs in limit_tiers:
            if placed_group: break

            for start_dt in candidate_datetimes:
                end_dt = start_dt + timedelta(minutes=dur)
                ex_date = start_dt.date()

                # ── Per-section daily exam limits ────────────────────────────────
                # Rule: max 3 exams/day, max 2 major (or 3 if fallback).
                # Minor slots available = 4 − major_count already scheduled.
                # Valid combos: (2 maj + 2 min) OR (1 maj + 3 min) OR (4 min).
                daily_limits_ok = True
                for e in group_exams:
                    sec = (e.get('section') or '').strip()
                    if not sec:
                        continue
                    is_major  = (e.get('subject_type') or 'Major') == 'Major'
                    cur_maj   = maj_count[sec][ex_date]
                    cur_min   = min_count[sec][ex_date]
                    cur_total = total_exam_count[sec][ex_date]
                    min_slots_left = 4 - cur_maj   # minor slots remaining after majors
                    if is_major and cur_maj >= major_limit:
                        daily_limits_ok = False; break
                    if not is_major and cur_min >= min_slots_left:
                        daily_limits_ok = False; break
                    if cur_total >= 4:
                        daily_limits_ok = False; break
                if not daily_limits_ok: continue


            # Section conflict: a section cannot sit two different exams at the same time
            # Also check for intra-group duplicates (e.g. same section taking same subject twice)
                group_sections = [e.get('section').strip() for e in group_exams if e.get('section') and e.get('section').strip()]
                intra_group_ok = len(group_sections) == len(set(group_sections))
            
                section_ok = intra_group_ok and all(
                    section_free(e.get('section'), start_dt, end_dt)
                    for e in group_exams
                )
                if not section_ok: continue

                # Capacity requirements per exam
                req_caps = []
                for e in group_exams:
                    stu_cnt = int(e.get('section_student_count') or 0)
                    inst_cap = int(e.get('institute_capacity_default') or 40)
                    req_caps.append(stu_cnt if stu_cnt > 0 else inst_cap)
                min_req_cap = min(req_caps) if req_caps else 40

                # Filter unbooked rooms with sufficient capacity
                free_rooms = [r for r in rooms if room_free(r['id'], start_dt, end_dt) and int(r.get('capacity', 0) or 0) >= min_req_cap]
                if len(free_rooms) < n_needed: continue

                candidate_insts = []
                import re as _re
                for i in instructors:
                    if not inst_free(i['id'], start_dt, end_dt): continue
                    if not inst_available(i['id'], start_dt, end_dt): continue
                
                    # Rule 2: Academic Integrity - Strict Self-Proctoring Exclusion
                    raw_subs = i.get('subjects_taught') or ''
                    if raw_subs.strip():
                        subs_taught = {s.strip().lower() for s in _re.split(r'[,|;]', raw_subs) if s.strip()}
                        is_teaching_this_course = False
                        for e in group_exams:
                            s_name = (e.get('subject_name') or '').strip().lower()
                            s_code = (e.get('subject_code') or '').strip().lower()
                            s_id   = str(e.get('subject_id') or '')
                            if s_name and (s_name in subs_taught or any(s_name == sub or sub in s_name for sub in subs_taught)):
                                is_teaching_this_course = True
                                break
                            if s_code and s_code in subs_taught:
                                is_teaching_this_course = True
                                break
                            if s_id and s_id in subs_taught:
                                is_teaching_this_course = True
                                break
                        if is_teaching_this_course:
                            continue
                
                    # Rule 1: Max consec
                    if get_consecutive_hours(i['id'], ex_date, start_dt, end_dt) > max_consec_hrs: continue

                    # Rule 3: Max daily proctor hours (strictly enforced per tier)
                    if inst_daily_hours[i['id']][ex_date] + dur_hrs > allowed_daily_hrs + 1e-5: continue
                
                    candidate_insts.append(i)
            
                if len(candidate_insts) < n_needed: continue

                # Fair workload balancing:
                # 1. Fewest daily hours already scheduled today
                # 2. Fewest cumulative hours across the entire examination period
                # 3. Least recently assigned (or never assigned: -1)
                candidate_insts.sort(key=lambda inst: (
                    inst_daily_hours[inst['id']][ex_date],
                    inst_total_hours[inst['id']],
                    inst_last_assigned[inst['id']]
                ))

                # Assignment
                assigned_this_slot = True
                temp_schedule = []
                available_rooms = list(free_rooms)
                available_insts = list(candidate_insts)
            
                for idx, exam in enumerate(group_exams):
                    # PWD room constraint
                    exam_room = None
                    exam_inst = None
                
                    # Match suitable inst with suitable room
                    # available_insts is already sorted by fairness (least loaded first)
                    needed_cap = req_caps[idx] if idx < len(req_caps) else 40
                    for i in available_insts:
                        last_b = inst_last_building[i['id']].get(ex_date)
                        for r in available_rooms:
                            # Strict room capacity verification
                            if int(r.get('capacity', 0) or 0) < needed_cap: continue
                            if i.get('is_pwd') and not r.get('is_pwd_accessible'): continue
                            if last_b:
                                last_end, b_name = last_b
                                if b_name != r.get('building'):
                                    if (start_dt - last_end).total_seconds() < travel_buffer * 60:
                                        continue
                            exam_room = r
                            exam_inst = i
                            break
                        if exam_room and exam_inst:
                            break
                
                    if exam_room and exam_inst:
                        available_rooms.remove(exam_room)
                        available_insts.remove(exam_inst)
                        temp_schedule.append({
                            'exam': exam,
                            'room': exam_room,
                            'inst': exam_inst
                        })
                    else:
                        assigned_this_slot = False
                        break
            
                if assigned_this_slot:
                    for item in temp_schedule:
                        e = item['exam']
                        r = item['room']
                        i = item['inst']
                        section = e.get('section') or ''
                        is_major = (e.get('subject_type') or 'Major') == 'Major'
                    
                        scheduled.append({
                            'exam_id': e['id'],
                            'subject_name': e.get('subject_name', 'Unknown Subject'),
                            'section': e.get('section', ''),
                            'room_id': r['id'],
                            'instructor_id': i['id'],
                            'instructor_name': i['name'],
                            'exam_date_time': start_dt,
                        })
                        room_cal[r['id']].append((start_dt, end_dt))
                        inst_cal[i['id']].append((start_dt, end_dt))
                        inst_consecutive_hours[i['id']][ex_date].append((start_dt, end_dt))
                        inst_daily_hours[i['id']][ex_date] += dur_hrs
                        inst_total_hours[i['id']] += dur_hrs
                        inst_last_assigned[i['id']] = assign_counter[0]
                        assign_counter[0] += 1
                        inst_last_building[i['id']][ex_date] = (end_dt, r.get('building'))
                        if section:
                            sec_key = section.strip()
                            section_cal[sec_key].append((start_dt, end_dt))
                            if is_major:
                                maj_count[sec_key][ex_date] += 1
                            else:
                                min_count[sec_key][ex_date] += 1
                            total_exam_count[sec_key][ex_date] += 1
                
                    subject_locked_slot[subj_key] = start_dt
                    placed_group = True
                    break

        if not placed_group:
            for exam in group_exams:
                section = exam.get('section') or ''
                failed.append({
                    'exam_id': exam['id'],
                    'subject_name': exam.get('subject_name'),
                    'section': exam.get('section'),
                    'reason': f'No slot found satisfying all constraints for {n_needed} sections simultaneously.'
                })

    return {'scheduled': scheduled, 'failed': failed}
