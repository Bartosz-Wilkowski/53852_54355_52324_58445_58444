-- Script to revoke DROP privileges from all users for the user_auth database
SET @sql = NULL;

-- Create a query to gather all REVOKE DROP commands for users having access to user_auth
SELECT GROUP_CONCAT(CONCAT('REVOKE DROP ON `user_auth`.* FROM `', user, '`@`', host, '`;') SEPARATOR ' ')
INTO @sql
FROM mysql.db
WHERE db = 'user_auth' AND user != 'root' AND user != 'mysql.sys';

-- Prepare the script for execution
PREPARE stmt FROM @sql;
-- Execute the script
EXECUTE stmt;
-- Deallocate resources
DEALLOCATE PREPARE stmt;

-- (Optional) Check user privileges after making changes
SELECT user, host, db, GROUP_CONCAT(privilege_type SEPARATOR ', ') AS privileges
FROM information_schema.schema_privileges
WHERE privilege_type = 'DROP' AND db = 'user_auth'
GROUP BY user, host, db;