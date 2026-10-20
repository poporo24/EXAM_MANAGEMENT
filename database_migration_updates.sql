-- ====================================================================
-- CCA EXAM MANAGEMENT SYSTEM - DATABASE MIGRATION SCRIPT
-- ====================================================================
-- If you pulled updates to another computer (e.g. your laptop),
-- you can run these SQL statements in phpMyAdmin under:
-- Database: cca_exam_management_db
--
-- Note: The Python application also runs an automatic schema check
-- on startup (`ensure_database_schema()`), but running this SQL script
-- directly in phpMyAdmin ensures your database is 100% prepared.
-- ====================================================================

USE `cca_exam_management_db`;

-- 1. Create the `exam_archives` table for Historical Exam Records & PDF snapshots
CREATE TABLE IF NOT EXISTS `exam_archives` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `academic_year` varchar(50) NOT NULL,
  `exam_term` varchar(50) NOT NULL,
  `exam_semester` varchar(50) NOT NULL,
  `archive_title` varchar(150) NOT NULL,
  `total_exams` int(11) DEFAULT 0,
  `total_proctors` int(11) DEFAULT 0,
  `total_sections` int(11) DEFAULT 0,
  `period_start` date DEFAULT NULL,
  `period_end` date DEFAULT NULL,
  `archived_at` datetime DEFAULT current_timestamp(),
  `archived_by` int(11) DEFAULT NULL,
  `archived_by_name` varchar(100) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `snapshot_data` longtext NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 2. Add `max_daily_proctor_hrs` to `system_settings` (if missing)
-- If your MySQL doesn't support 'IF NOT EXISTS' for columns, you can omit 'IF NOT EXISTS'
ALTER TABLE `system_settings` 
  ADD COLUMN IF NOT EXISTS `max_daily_proctor_hrs` float NOT NULL DEFAULT 4.0;

-- 3. Add Schedule Publication state flags to `system_settings` (if missing)
ALTER TABLE `system_settings` 
  ADD COLUMN IF NOT EXISTS `schedule_published` tinyint(1) NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS `schedule_published_at` datetime DEFAULT NULL;
