# Requirement Specification Analysis: ExamScheduler System

## 1. System Overview
The ExamScheduler is an automated academic examination scheduling platform designed to streamline timetable generation, eliminate room and time conflicts, manage proctor assignments, and distribute personalized schedules to all academic stakeholders. The platform provides specialized dashboards for administrators, departmental staff, instructors, invigilators, and students to ensure smooth and transparent examination operations across the entire institution.

---

## 2. Stakeholders and User Roles
The platform supports seven distinct user groups tailored to the institution's examination workflow:
1. **Super Administrator:** The highest-level system authority responsible for user account oversight, role assignment, student registration approval, security maintenance, and master system settings.
2. **System Administrator (Admin):** The academic operations manager responsible for course records, room inventories, constraint rules, automated schedule generation, manual conflict resolution, and official schedule publication.
3. **Department Secretary:** The academic office staff member responsible for tracking daily exam flow, monitoring proctor attendance, managing test paper handouts and returns, and dispatching standby relievers.
4. **Faculty / Instructor:** Academic teaching personnel who verify subject enrollments, check scheduled exam slots, submit exam duration requests, and are strictly restricted from proctoring their own course exams.
5. **Proctor (Exam Invigilator):** Examination supervisors who submit working availability, confirm assigned exam shifts and room locations, sign for exam materials, and report emergency absences.
6. **Student (Regular / Enrolled):** Registered students who access conflict-free personal exam timetables, check exam rooms and seat allocations, print official exam passes, and receive real-time updates.
7. **Irregular / Public Student (Guest Viewer):** Non-logged-in students and irregular examinees who access the public portal to search and view exam timetables by class section across different year levels.

---

## 3. General & Core Authentication Modules
These core modules provide secure and accessible platform entry for all system participants:

* **User Authentication Module:** Authenticates login credentials for administrators, faculty members, proctors, secretaries, and students to grant secure access to their designated dashboard features.
* **Student Self-Registration Module:** Allows new students to submit their registration details including name, email, password, institute, and section for administrative review and approval.
* **Password Change Module:** Assists logged-in users in updating and managing their account passwords securely after confirming their current password.
* **Password Reset Module:** Enables users who forgot their credentials to securely reset their password via a time-sensitive link delivered directly to their registered email address.
* **Session Security Module:** Automatically terminates inactive sessions after twenty minutes of inactivity to prevent unauthorized access and protect user account data on shared campus computers.
* **Role-Based Redirection Module:** Automatically routes each authenticated user to their role-specific dashboard immediately after successful login.
* **System Notification Bell Module:** Displays unread alert badges, message counts, and real-time operational updates directly in the navigation bar for active users.
* **Terms and Privacy Information Module:** Provides public access to the platform terms of service and institutional data privacy compliance guidelines for all campus visitors.

---

## 4. Functional Requirements by User Role

### 4.1 Super Administrator Module
This module provides master-level authority over system accounts, access privileges, global security parameters, and institutional audit trails.

* **User Account Management Module:** Allows the super administrator to view all registered accounts and modify user profile details, email addresses, institute affiliations, or role assignments.
* **Student Registration Approval Module:** Enables the super administrator to review pending student registrations and either approve or reject them before granting platform access.
* **User Account Deletion Module:** Allows the super administrator to permanently delete obsolete user accounts while protecting active administrative profiles from accidental self-deletion.
* **Administrative Password Reset Module:** Enables the super administrator to immediately reset passwords directly for any user experiencing account access issues.
* **System Email Configuration Module:** Allows the super administrator to configure and test outgoing system email credentials used for automated alerts and password resets.
* **System Audit Log Module:** Records all critical administrative activities, timetable modifications, and security events with timestamps and IP addresses for complete institutional accountability.

---

### 4.2 System Administrator Module (Admin)
This module is dedicated to overseeing platform operations, academic course records, room inventories, constraint configuration, automated timetable generation, and operational reporting.

* **Administrative Dashboard Module:** Displays a real-time operational summary of total subjects, active rooms, registered proctors, scheduled exams, pending approvals, and unresolved conflicts.
* **Manage Subjects Module:** Allows administrators to input and update subject details, including course code, assigned faculty, academic institute, and student population.
* **Subject CSV Import Module:** Enables administrators to upload bulk subject and curriculum records quickly using standardized spreadsheet templates.
* **Manage Student Data Module:** Enables management of student enrollment records, section assignments, and account statuses to organize student-subject mapping and eliminate examination conflicts.
* **Faculty and Proctor Management Module:** Allows administrators to manage faculty schedules, assign proctors, verify instructor availability, and ensure instructors are never assigned to proctor their own examinations.
* **Faculty CSV Import Module:** Enables administrators to import instructor profiles and teaching subject assignments in bulk using standardized spreadsheet files.
* **Room Management Module:** Enables administrators to define examination rooms, seating capacities, campus buildings, and wheelchair accessibility statuses to support efficient room allocation during exam scheduling.
* **Room CSV Import Module:** Allows administrators to upload complete institutional classroom inventories and seating capacities from spreadsheet templates.
* **Institute and Department Management Module:** Allows administrators to add, edit, and organize academic institutes, colleges, and default classroom seating capacities.
* **Proctor Availability Configuration Module:** Allows administrators to configure, adjust, or bulk-assign available dates and working time shifts for all registered proctors.
* **Standby Reliever Management Module:** Allows administrators to designate standby invigilators who can quickly replace absent proctors during examination sessions.
* **Rule-Based Configuration Module:** Allows administrators to configure active scheduling rules, including zero student exam overlaps, room capacity compliance, faculty restrictions, and daily exam caps.
* **Exam Scheduling Module:** Automatically generates conflict-free examination schedules by processing subject data, faculty schedules, room availability, and predefined institutional rules.
* **Sister-Section Synchronization Module:** Automatically aligns examination schedules so that multiple class sections taking the same course subject sit for the examination simultaneously to eliminate test question leaks.
* **Intelligent Resource Suggestion Module:** Provides smart recommendations for available examination rooms and proctors during manual timetable adjustments.
* **Interactive Schedule Editor Module:** Allows administrators to manually modify exam dates, times, rooms, and proctors with live conflict detection.
* **Schedule Conflict Resolution Module:** Automatically detects and resolves remaining scheduling overlaps through targeted rescheduling algorithms.
* **Schedule Approval Module:** Allows administrators to review generated schedules, apply necessary revisions, and finalize official examination schedules before public release.
* **Dual-Authorization Schedule Reset Module:** Enables administrators to submit or approve timetable reset requests requiring dual-admin validation before clearing scheduled examination records.
* **Batch Section Printing Module:** Generates consolidated, printable examination schedules organized by student section for institutional distribution.
* **Master Timetable PDF Export Module:** Exports complete master examination schedules into formatted PDF documents ready for official posting and archiving.
* **Reports Generation Module:** Generates official reports, printable schedules, and timetable summaries categorized by subject, room, faculty, proctor absence, or exam collection status.
* **Academic Term and Period Configuration Module:** Allows administrators to define the current academic year, examination period dates, active semester, and scheduling time boundaries.
* **Notification Module:** Sends schedule announcements, release alerts, and urgent updates to faculty members and students regarding examination details and schedule changes.

---

### 4.3 Department Secretary Module
This module enables academic office staff to monitor daily exam operations, manage test paper logistics, track proctor attendance, and dispatch standby invigilators.

* **Department Operations Dashboard Module:** Displays real-time daily examination timetables, assigned proctors, and room schedules specific to the secretary's academic department.
* **Test Paper Distribution Tracking Module:** Logs the checkout and handover of printed examination questionnaires and test booklets to assigned proctors before exam sessions start.
* **Test Paper Return Tracking Module:** Records the return and custody verification of completed student answer sheets, remaining exam papers, and signed proctor attendance sheets after exams conclude.
* **Proctor Attendance Monitoring Module:** Tracks proctor reporting on examination day and flags missing or delayed invigilators in real time.
* **Emergency Absence Recording Module:** Records sudden proctor absences and logs submitted reasons to maintain an official administrative record of duty disruptions.
* **Standby Reliever Dispatch Module:** Assigns available standby proctors immediately to uncovered examination rooms with a single click to prevent testing delays.
* **Department Document Printing Module:** Generates printable classroom door postings, room seating sheets, and student attendance rosters for departmental examination rooms.
* **Proctor Absence History Review Module:** Displays cumulative logs of proctor absences to help departmental leadership monitor duty compliance.
* **Secretary Password Management Module:** Enables department secretaries to update their account passwords securely directly from their dashboard.

---

### 4.4 Faculty / Instructor Module
This module allows instructors to review course exam schedules, verify examinee rosters, submit exam constraints, and maintain academic integrity.

* **View Exam Schedule Module:** Displays confirmed examination dates, time windows, durations, and assigned rooms for all courses taught by the instructor.
* **Proctor Conflict Exclusion Verification Module:** Confirms that the scheduling engine automatically prevents instructors from invigilating their own course examinations.
* **Examinee Roster Verification Module:** Allows instructors to review the official list of enrolled students and class sections scheduled for their subject exams.
* **Exam Parameter Submission Module:** Enables instructors to submit special exam duration requirements, preferred schedule slots, or equipment needs prior to timetable generation.
* **Examination Update Alerts Module:** Delivers instant dashboard alerts and email notifications whenever an instructor's course exam schedule or room assignment is updated.

---

### 4.5 Proctor Module (User)
This module is designed for proctors responsible for supervising examinations, managing working availability, and logging room proceedings.

* **View Exam Schedule Module:** Displays assigned examination schedules, including subject name, date, exact start and end times, and room details.
* **View Proctor Assignment Module:** Shows proctors their designated proctoring responsibilities, assigned rooms, and cumulative duty hours.
* **Manage Proctor Availability:** Proctors can manage and submit their time and date availability windows before the automated scheduling engine generates timetables.
* **Emergency Absence Reporting Module:** Allows proctors to notify the department secretary of unexpected absences with an explanation so a standby reliever can be assigned immediately.
* **Exam Material Handover Verification Module:** Confirms the physical receipt of examination envelopes from the department secretary and logs the return of completed answer sheets.
* **Receive Notifications Module:** Provides faculty and proctors with real-time updates regarding duty assignments, examination schedule changes, and official announcements.

---

### 4.6 Student Module (User)
This module supports registered students in accessing their personalized examination schedules, room locations, and printable examination passes.

* **View Exam Schedule Module:** Allows students to access their personalized, conflict-free subject examination schedules, room assignments, and exam dates.
* **Room and Venue Allocation Module:** Shows assigned examination rooms, building locations, and floor directions to ensure orderly arrival on exam days.
* **Printable Exam Timetable and Slip Module:** Allows students to view, download, and print their official examination timetable slip to serve as an entry pass during exam week.
* **Notification Module:** Sends updates regarding exam schedule releases, emergency room revisions, and important institutional announcements.
* **Student Profile and Security Module:** Enables students to view their registration information, check account approval status, and update their account password.

---

### 4.7 Irregular / Public Student Module (Guest Portal)
This module provides open schedule access for non-registered students, transferees, and students taking irregular subject loads across multiple sections.

* **Public Timetable Viewing Module:** Allows irregular students and public guests to view officially published examination timetables without logging into an account.
* **Section Timetable Search Module:** Enables users to select any class section from an organized dropdown list to view that section's complete exam schedule.
* **Cross-Section Subject Lookup Module:** Allows irregular students enrolled in multiple sections to find exam schedules and room assignments across different class groups.
* **Exam Overlap Checking Module:** Helps irregular students verify if exams for subjects taken across different year levels share conflicting time slots.
* **Mobile-Responsive Timetable Viewer Module:** Provides an accessible, mobile-friendly schedule layout allowing students to view or print their schedules from any mobile or desktop device.

---

## 5. Non-Functional Requirements
These criteria define the quality standards, reliability benchmarks, and operational constraints of the platform:

* **Performance:** The automated scheduling engine must generate and optimize complete institutional examination timetables within a few seconds without causing system timeouts.
* **Data Accuracy and Conflict Prevention:** The system must strictly prevent double-booking for any student section, classroom, or proctor across all scheduled examination slots.
* **Usability:** The interface must use simple terms, intuitive navigation, and clean layouts that work seamlessly across desktop computers and mobile devices.
* **Security:** The system must enforce role-based access control, secure password hashing, protected sessions, and encrypted data transmission across all user interactions.
* **Reliability and Availability:** The system must remain consistently accessible during high-traffic timetable release periods and safeguard data through pooled database transactions.
* **Maintainability:** The modular system architecture must allow easy updates, straightforward database maintenance, and future functional expansions without disrupting existing services.
