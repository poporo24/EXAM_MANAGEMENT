# CCA Exam Management System — Official Demonstration Guide & Presentation Script

## 📌 Executive Summary
The **CCA Exam Management System** is an automated scheduling, resource allocation, and proctor governance platform designed for City College of Angeles (CCA). It solves complex academic examination bottlenecks:
- Multi-institute room & proctor conflict avoidance
- Automatic enforcement of academic constraints (max 2 majors/day, PWD room accessibility, travel buffers)
- **Cross-Institute Subject Aliasing & Content Linking** (e.g. Major in ICSLIS vs. Minor in IBM/IEAS sharing the same exam slot)
- Real-time role-based access for Admins, Proctors, Department Secretaries, and Students.

---

## 🔑 Demonstration Accounts & Credentials Matrix

| Role | Full Name | Email Login | Default Password | Institute / Dept |
|---|---|---|---|---|
| **Super Admin** | CCA Super Admin | `superadmin@cca.edu.ph` | *(Password set at registration)* | College-Wide |
| **Admin** | CCA Admin | `admin@cca.edu.ph` | *(Password set at registration)* | College-Wide |
| **Proctor / Faculty** | Kurt Salonga | `kurt.salonga@cca.edu.ph` | *(Password set at registration)* | ICSLIS |
| **Proctor / Faculty** | Izzy Padoc | `izzy.padoc@cca.edu.ph` | *(Password set at registration)* | ICSLIS |
| **Department Secretary** | CCA Secretary | `secretary@cca.edu.ph` | *(Password set at registration)* | All Institutes |
| **Student** | Jergie Toti | `jergietoti@gmail.com` | *(Password set at registration)* | ICSLIS / Section C101 |
| **Student** | John Paul Baltazar | `jpbaltazar24@cca.edu.ph` | *(Password set at registration)* | ICSLIS |

---

## 🎬 Live Demonstration Flow (8-Stage Presentation)

### Stage 1: System Overview & Admin Dashboard
1. **Navigate to:** `http://127.0.0.1:9999/`
2. **Action:** Log in as Administrator (`admin@cca.edu.ph`).
3. **Talking Points:**
   - Real-time KPI counter: Total Scheduled Exams, Active Proctors, Available Classrooms, and Conflict Alerts.
   - Institute-level distribution metrics.
   - Quick navigation to Schedule, Subjects, Institutes, Reports, and System Settings.

---

### Stage 2: Showcase Feature — Cross-Institute Subject Aliasing
> **The Problem:** In CCA, the exact same exam syllabus is taught under different course codes and names across colleges:
> - **ICSLIS:** `Information Technology 2` (`IT201`) — *Major Subject*
> - **IBM:** `IT for Business Management` (`BUS105`) — *Minor Subject*
> - **IEAS:** `Computing & Informatics` (`ENG200`) — *Minor Subject*
> Without Content Linking, the system would schedule these at different times, requiring multiple proctors and duplicating exam room usage.

1. **Navigate to:** `http://127.0.0.1:9999/subjects`
2. **Showcase Actions:**
   - Point out the **"Subject Alias Groups"** visual panel displaying **Alias Group #1** with all 3 linked subjects.
   - Point out the badges: Course Codes (`IT201`, `BUS105`, `ENG200`), Institute tags, and Common tags.
   - Demonstrate the **Multi-Select Link Form**:
     - Check 2 or more subjects from the interactive checklist.
     - Notice the live counter: *"2 subjects selected"*.
     - Click **Link Selected** to instantly bundle them.
   - Demonstrate the **Unlink** button: Click *Unlink* on a subject to show seamless detachment and dynamic group dissolution if fewer than 2 remain.

---

### Stage 3: AI-Assisted Auto-Scheduler & Constraint Engine
1. **Navigate to:** `http://127.0.0.1:9999/schedule`
2. **Showcase Actions:**
   - Show the Examination Period selector (e.g. August 24 – August 29, 2026).
   - Click **Run Auto-Scheduler**.
3. **Talking Points on Automated Constraints:**
   - **Content-Grouped Synchronicity:** All aliased subjects are locked to the exact same timeslot.
   - **Student Workload Safety:** No section is assigned more than 2 Major examinations on a single calendar day.
   - **Faculty Subject Neutrality:** Proctors are never assigned to invigilate subjects they teach.
   - **PWD & Mobility Compliance:** PWD instructors are strictly assigned ground-floor or elevator-accessible rooms.
   - **Campus Travel Buffer:** A 15-minute inter-building travel window prevents proctor sprint overlaps.

---

### Stage 4: Interactive Schedule Matrix & Drag/Manual Conflict Check
1. **Navigate to:** `http://127.0.0.1:9999/schedule`
2. **Showcase Actions:**
   - View the calendar/grid view showing rooms vs. time intervals.
   - Click **Edit Exam** on any slot.
   - Change the assigned room or proctor to an intentionally conflicting slot.
   - Observe the **real-time Conflict Prevention Modal**: The system detects the clash and blocks invalid overrides.

---

### Stage 5: Proctor Portal & Availability Submission
1. **Action:** Log out and log in as Proctor (`kurt.salonga@cca.edu.ph`).
2. **Navigate to:** `http://127.0.0.1:9999/proctor/dashboard`
3. **Showcase Actions:**
   - View assigned invigilation schedule with room numbers, subject details, and time.
   - Demonstrate the **Availability Setter**: Proctor selects dates/time windows where they are available or requests absence.
   - Notice the total invigilation hours counter ensuring equity among faculty members.

---

### Stage 6: Secretary Exam Paper Distribution & Collection
1. **Action:** Log out and log in as Secretary (`secretary@cca.edu.ph`).
2. **Navigate to:** `http://127.0.0.1:9999/secretary`
3. **Showcase Actions:**
   - Real-time exam paper lifecycle tracking:
     - 🟡 **Pending Collection**
     - 🔵 **Collected by Proctor**
     - 🟢 **Returned to Department / Secured**
   - Click **Mark Collected** and **Mark Returned** with timestamped audit logging.

---

### Stage 7: Student Personalized Examination Timetable
1. **Action:** Log out and log in as Student (`jergietoti@gmail.com` or `student@test.com`).
2. **Navigate to:** `http://127.0.0.1:9999/student/timetable`
3. **Showcase Actions:**
   - Filtered view showing only exams relevant to the student's registered section/courses.
   - Clear display of Room Number, Floor/Building, Subject Code, Date, and Time.
   - Print/Download PDF-ready format for student mobile viewing.

---

### Stage 8: Reports, Analytics & Data Export
1. **Action:** Log back in as Admin (`admin@cca.edu.ph`).
2. **Navigate to:** `http://127.0.0.1:9999/reports`
3. **Showcase Actions:**
   - **Proctor Hours Distribution Report:** Shows proctoring workload fairness.
   - **Room Utilization Efficiency Report:** Highlights room peak-time usage.
   - **Student Exam Density Analysis:** Confirms zero students exceed 2 majors per day.
   - **CSV/Excel Export:** One-click export for CHED/Institutional compliance.
