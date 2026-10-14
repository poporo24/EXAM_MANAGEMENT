# CCA Exam Management System – Complete End-to-End Demonstration Guide

## 🎯 Executive Summary
The **CCA Exam Management System** is an automated scheduling, resource allocation, and proctor governance platform designed for City College of Angeles (CCA). It provides a full-suite solution across 5 user roles to solve complex academic examination bottlenecks.

## 👥 Demonstration Accounts Matrix
| Role | Recommended Demo Account | Permissions |
|---|---|---|
| **Super Admin** | `superadmin@cca.edu.ph` | Full system control, manages users. |
| **Admin** | `admin@cca.edu.ph` | Schedules, manages data, resolves conflicts. |
| **Secretary** | `secretary@cca.edu.ph` | Tracks exam papers and manages proctor absences. |
| **Proctor** | `instructor@cca.edu.ph` | Views assigned exams and assigned availability. |
| **Student** | `student@cca.edu.ph` | Views personal examination timetable. |

---

## 🎬 9-Stage Demonstration Flow

### Stage 1: Super Admin System Initialization
1. Log in as **Super Admin**.
2. Navigate to **User Management**. Show how to create accounts for all 5 roles.
3. Explain how roles compartmentalize access to ensure security.

### Stage 2: Data Import & Availability Assignment
1. Log in as **Admin**.
2. Go to **Dashboard** -> Showcase **CSV Import Modals**.
3. Highlight that the Instructor CSV reads `availability` (e.g., "Mon 07:00-12:00") directly.
4. Go to **Faculty** -> **Proctor Availability**. Show how admins lock in specific availability hours for faculty.

### Stage 3: Cross-Institute Subject Aliasing
1. Go to **Subjects**.
2. Explain the curriculum problem: Identical syllabi under different codes (ICSLIS `IT201` vs IBM `BUS105`).
3. Select both subjects, click **Link Selected**. Show the creation of an **Alias Group**.

### Stage 4: The AI Auto-Scheduler Engine
1. Go to **Schedule**.
2. Click **Run Auto-Scheduler**.
3. Detail the constraints checked instantly:
   - **Student Wellness:** Max 2 majors/day.
   - **Instructor Neutrality:** Cannot proctor own subject.
   - **Accessibility:** PWD instructors restricted to 1st floor.
   - **Logistics:** 15-minute inter-building travel buffer.
   - **Availability:** Only assigns within Admin-approved hours.

### Stage 5: Manual Overrides & Live Conflict Detection
1. On the **Schedule**, click an exam to manually Edit.
2. Intentionally create a conflict (book a busy room or unavailable proctor).
3. Show the **Error Modal**, proving the system intercepts human error.

### Stage 6: The Proctor Experience
1. Log in as **Proctor**.
2. Show the **Proctor Dashboard**.
3. Highlight the **My Assigned Availability** widget, showing exactly what the Admin cleared them for.
4. Show the **Report Absence** button for emergencies.

### Stage 7: Secretary Paper Lifecycle & Absences
1. Log in as **Secretary**.
2. Showcase paper tracking: **Pending** -> **Collected** -> **Returned**.
3. Show the **Absence Reports** tab to assign Relievers when proctors call in sick.

### Stage 8: Student Portal
1. Log in as **Student**.
2. Show the personalized **Timetable**, filtered only for their section.
3. Show the PDF/Print functionality.

### Stage 9: Reports & Analytics
1. Log back in as **Admin**.
2. Go to **Reports** to showcase Proctor Hours equity and Room Utilization.
3. Click **Export** to demonstrate CHED/Administrative reporting compliance.
