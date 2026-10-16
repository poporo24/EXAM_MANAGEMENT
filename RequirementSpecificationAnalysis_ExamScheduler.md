# Requirement Specification Analysis: ExamScheduler System

## 1. System Overview
The ExamScheduler is an automated academic examination scheduling platform designed to streamline timetable generation, eliminate room and time conflicts, manage proctor assignments, and distribute personalized schedules to all academic stakeholders. The platform provides specialized dashboards for administrators, departmental staff, instructors, invigilators, and students to ensure smooth and transparent examination operations across the entire institution.

---

## 2. Stakeholders and User Roles
The system supports seven distinct user groups tailored to the institution's examination workflow:
1. **Super Administrator:** The highest-level system authority responsible for user account oversight, role assignment, student registration approval, security maintenance, and master system settings.
2. **System Administrator (Admin):** The academic operations manager responsible for course records, room inventories, constraint rules, automated schedule generation, manual conflict resolution, and official schedule publication.
3. **Department Secretary:** The academic office staff member responsible for tracking daily exam flow, monitoring proctor attendance, managing test paper handouts and returns, and dispatching standby relievers.
4. **Faculty / Instructor:** Academic teaching personnel who verify subject enrollments, check scheduled exam slots, submit exam duration requests, and are strictly restricted from proctoring their own course exams.
5. **Proctor (Exam Invigilator):** Examination supervisors who submit working availability, confirm assigned exam shifts and room locations, sign for exam materials, and report emergency absences.
6. **Student (Regular / Enrolled):** Registered students who access conflict-free personal exam timetables, check exam rooms and seat allocations, print official exam passes, and receive real-time updates.
7. **Irregular / Public Student (Guest Viewer):** Non-logged-in students and irregular examinees who access the public portal to search and view exam timetables by class section across different year levels.

---

## 3. General & Core Authentication Modules
These core modules provide secure and accessible platform entry for all system participants.

* **User Authentication Module:** Allows registered administrators, secretaries, proctors, and students to log into their dedicated dashboards using their email address and secure password.
* **Student Self-Registration Module:** Allows new students to create an account by submitting their full name, email address, password, academic institute, and section for administrative approval.
* **Self-Service Password Reset Module:** Enables users who forgot their password to request a secure password-reset link sent directly to their registered email address.
* **Account Password Update Module:** Allows logged-in users to change their account password at any time by verifying their current password and entering a new one.
* **Role-Based Redirection Module:** Automatically routes each authenticated user to their role-specific dashboard immediately after successful login.
* **Session Security Module:** Automatically terminates inactive sessions to prevent unauthorized access and protect user account data on shared devices.
* **System Notification Bell Module:** Displays real-time alert badges, unread message counts, and schedule updates directly in the navigation bar for active users.
* **Terms and Privacy Information Module:** Provides public access to the platform terms of service and data privacy guidelines for all visitors.

---

## 4. Functional Requirements by User Role

### 4.1 Super Administrator Module
The Super Administrator module provides master-level control over system accounts, access privileges, and global security settings.

* **User Account Management Module:** Allows the super administrator to view all registered accounts and modify user profile details, email addresses, institute affiliations, or role assignments.
* **Student Registration Approval Module:** Enables the super administrator to review, approve, or reject pending student registrations before granting platform access.
* **User Account Deletion Module:** Allows the super administrator to permanently delete unnecessary user accounts while preventing accidental self-deletion.
* **Administrative Password Reset Module:** Enables the super administrator to immediately reset passwords for any user experiencing account access issues.
* **System Email Configuration Module:** Allows the super administrator to configure and test outgoing system email credentials used for automated alerts and password resets.

---

### 4.2 System Administrator Module
The System Administrator module provides complete academic data management, constraint configuration, automated timetable generation, and operational reporting tools.

* **Administrative Dashboard Module:** Displays a real-time operational summary of total subjects, active rooms, registered proctors, scheduled exams, pending approvals, and unresolved conflicts.
* **Subject Management Module:** Allows administrators to create, edit, search, filter, delete, and bulk-delete academic subjects and their assigned instructors.
* **Subject CSV Import Module:** Enables administrators to upload bulk subject and curriculum records quickly using standardized spreadsheet templates.
* **Institute and Department Management Module:** Allows administrators to add, edit, and organize academic institutes and colleges across the institution.
* **Course-to-Institute Linking Module:** Enables administrators to link or unlink specific subjects to appropriate academic institutes for structured curriculum organization.
* **Room and Facility Management Module:** Allows administrators to register examination rooms, set maximum seating capacities, specify campus buildings, and import room lists from CSV files.
* **Faculty Directory Management Module:** Enables administrators to maintain instructor profiles, toggle active or inactive employment statuses, and import faculty rosters via CSV files.
* **Individual Proctor Availability Module:** Allows administrators to set or modify available days, preferred time shifts, and maximum duty allocations for individual proctors.
* **Bulk Proctor Availability Module:** Enables administrators to apply standard availability days and time slots across all registered proctors in a single action.
* **Standby Reliever Management Module:** Allows administrators to designate standby invigilators who can quickly replace absent proctors during examination sessions.
* **Rule-Based Scheduling Configuration Module:** Enables administrators to configure scheduling constraints including room capacity limits, zero student exam overlaps, faculty restrictions, and daily exam caps.
* **Automated Exam Scheduling Engine:** Generates conflict-free examination timetables automatically by running scheduling algorithms that match subjects, rooms, proctors, and predefined rules.
* **Intelligent Resource Suggestion API:** Provides smart recommendations for available examination rooms and proctors during manual timetable adjustments.
* **Sister-Section Synchronization Module:** Automatically aligns examination schedules for shared course subjects across multiple class sections.
* **Interactive Schedule Editor Module:** Allows administrators to manually modify exam dates, times, rooms, and proctors with live conflict detection.
* **Schedule Conflict Resolution Module:** Automatically detects and resolves remaining scheduling overlaps through targeted rescheduling algorithms.
* **Schedule Reset Module:** Allows administrators to clear scheduled exam records and reset the timetable generator for a fresh scheduling run.
* **Student Account Supervision Module:** Enables administrators to approve, reject, deactivate, reactivate, and bulk-manage student profiles and section assignments.
* **Batch Section Printing Module:** Generates consolidated, printable examination schedules organized by student section for institutional distribution.
* **Master Timetable PDF Export Module:** Exports complete master examination schedules into formatted PDF documents ready for official posting and archiving.
* **Comprehensive Reports Module:** Generates detailed reports on proctor assignments, proctor absences, and test paper collection statuses.
* **Academic Term and Settings Module:** Allows administrators to define the current academic term, examination period dates, active semester, and scheduling parameters.
* **System-Wide Announcement Broadcast Module:** Sends urgent notices, schedule release alerts, and institutional announcements to all registered users.

---

### 4.3 Department Secretary Module
The Department Secretary module enables academic office staff to monitor daily exam operations, manage test paper logistics, track proctor attendance, and dispatch standby invigilators.

* **Department Operations Dashboard Module:** Displays real-time daily examination timetables, assigned proctors, and room schedules specific to the academic department.
* **Test Paper Distribution Tracking Module:** Logs the checkout and handover of printed examination questionnaires and test booklets to assigned proctors before exam sessions start.
* **Test Paper Retrieval and Return Module:** Records the return of completed student answer sheets, remaining exam papers, and signed proctor attendance sheets after exams conclude.
* **Proctor Attendance Logging Module:** Tracks proctor reporting status on examination day and flags missing or delayed invigilators in real time.
* **Emergency Absence Recording Module:** Records sudden proctor absences and logs submitted reasons to maintain an official record of duty disruptions.
* **Emergency Reliever Dispatch Module:** Assigns available standby proctors immediately to uncovered examination rooms to prevent testing delays.
* **Department Document Printing Module:** Generates printable classroom door postings, section schedules, and student attendance rosters for departmental examination rooms.
* **Proctor Absence History Review Module:** Displays cumulative logs of proctor absences to help departmental leadership monitor duty compliance.
* **Secretary Password Management Module:** Enables department secretaries to update their account passwords securely directly from their dashboard.

---

### 4.4 Faculty / Instructor Module
The Faculty module allows instructors to review course exam schedules, verify examinee rosters, submit exam constraints, and maintain academic integrity.

* **Course Exam Schedule Viewing Module:** Displays confirmed examination dates, time windows, durations, and assigned rooms for all courses taught by the instructor.
* **Proctor Conflict Exclusion Verification Module:** Confirms that the scheduling engine automatically prevents instructors from invigilating their own course examinations.
* **Examinee Roster Verification Module:** Allows instructors to review the official list of enrolled students and class sections scheduled for their subject exams.
* **Examination Parameter Submission Module:** Enables instructors to submit special exam duration requirements, equipment needs, or preferred schedule slots prior to timetable generation.
* **Exam Incident and Irregularity Reporting Module:** Allows instructors to report student conduct issues, cheating incidents, or paper discrepancies directly to the department secretary.
* **Schedule Update Alerts Module:** Delivers instant dashboard alerts and email notifications whenever an instructor's course exam schedule or room is updated.

---

### 4.5 Proctor / Exam Invigilator Module
The Proctor module assists invigilators in managing their assigned examination duties, submitting working availability, logging exam room proceedings, and reporting emergencies.

* **Proctor Duty Dashboard Module:** Displays a personal schedule of assigned proctoring duties, including exam dates, start and end times, room numbers, and subject titles.
* **Proctor Availability Submission Module:** Allows proctors to submit and update their available dates and preferred time shifts before the automated scheduling engine runs.
* **Duty Acknowledgment and Confirmation Module:** Enables proctors to confirm receipt of their assigned invigilation duties ahead of examination day.
* **Emergency Absence Reporting Module:** Allows proctors to notify the department secretary of unexpected absences with an explanation so a standby reliever can be assigned.
* **Exam Material Handover Verification Module:** Confirms the receipt of official examination envelopes from the secretary and logs the return of completed answer sheets.
* **Proctor Real-Time Notifications Module:** Sends immediate alerts to proctors regarding duty assignments, room adjustments, and schedule reminders.

---

### 4.6 Student Module (Registered Student)
The Student module provides registered students with personal, conflict-free examination schedules, room locations, and official printable permits.

* **Personalized Exam Timetable Module:** Displays a conflict-free examination schedule showing exact dates, starting times, end times, and subjects for the student's enrolled section.
* **Room and Venue Allocation Module:** Shows assigned examination rooms, building locations, and seating directions to ensure orderly arrival on exam days.
* **Printable Exam Timetable and Slip Module:** Allows students to print their official examination timetable slip to serve as an entry pass during exam week.
* **Real-Time Student Notification Module:** Alerts students immediately about published timetables, emergency room changes, and official school announcements.
* **Student Profile and Security Module:** Enables students to view their registration information, check account approval status, and update their password.

---

### 4.7 Irregular / Public Student Module (Guest Portal)
The Irregular / Public Student module provides open schedule access for non-registered students, transferees, and students taking irregular subject loads.

* **Public Timetable Access Module:** Allows irregular students and public guests to view published examination timetables without logging into an account.
* **Section Timetable Search Module:** Enables users to select any class section from an organized dropdown list to view that section's complete exam schedule.
* **Cross-Section Subject Lookup Module:** Allows irregular students enrolled in multiple sections to find exam schedules and room assignments across different class groups.
* **Exam Overlap Checking Module:** Helps irregular students verify if exams for subjects taken across different year levels share conflicting time slots.
* **Mobile-Responsive Timetable Viewer Module:** Provides an accessible, mobile-friendly schedule layout allowing students to view or print their schedules from any mobile or desktop device.

---

## 5. Non-Functional Requirements
These criteria define the quality standards, reliability benchmarks, and operational constraints of the platform.

* **Performance:** The automated scheduling engine must generate and optimize complete institutional examination timetables within a few minutes without causing system timeouts.
* **Data Accuracy and Conflict Prevention:** The system must strictly prevent double-booking for any student section, classroom, or proctor across all scheduled examination slots.
* **Usability:** The interface must use simple terms, intuitive navigation, and clean layouts that work seamlessly across desktop computers and mobile devices.
* **Security:** The system must enforce role-based access control, secure password hashing, protected sessions, and encrypted data transmission across all user interactions.
* **Reliability and Availability:** The system must remain consistently accessible during high-traffic timetable release periods and safeguard data through regular database backups.
* **Maintainability:** The modular system architecture must allow easy updates, straightforward database maintenance, and future functional expansions without disrupting existing services.
