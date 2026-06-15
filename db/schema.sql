CREATE TABLE cv_results (
	id INTEGER NOT NULL, 
	user_id VARCHAR(64), 
	gesture_id VARCHAR(64) NOT NULL, 
	accuracy FLOAT NOT NULL, 
	band VARCHAR(16) NOT NULL, 
	incorrect_points JSON NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE INDEX ix_cv_results_user_id ON cv_results (user_id);

CREATE TABLE lessons (
	id VARCHAR(64) NOT NULL, 
	title VARCHAR(120) NOT NULL, 
	description VARCHAR(500) NOT NULL, 
	difficulty VARCHAR(16) NOT NULL, 
	scenario_tag VARCHAR(32), 
	tags JSON NOT NULL, 
	gesture_ids JSON NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE routines (
	id VARCHAR(64) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	description VARCHAR(500) NOT NULL, 
	scenario_tag VARCHAR(32) NOT NULL, 
	created_by VARCHAR(64), 
	is_custom BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE users (
	id VARCHAR(64) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	role VARCHAR(16) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE educator_groups (
	id VARCHAR(64) NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	owner_user_id VARCHAR(64) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(owner_user_id) REFERENCES users (id)
);

CREATE INDEX ix_educator_groups_owner_user_id ON educator_groups (owner_user_id);

CREATE TABLE profiles (
	id VARCHAR(64) NOT NULL, 
	user_id VARCHAR(64) NOT NULL, 
	display_name VARCHAR(120) NOT NULL, 
	avatar VARCHAR(32) NOT NULL, 
	age_group VARCHAR(16) NOT NULL, 
	role VARCHAR(16) NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_profiles_user_id ON profiles (user_id);

CREATE TABLE routine_steps (
	id INTEGER NOT NULL, 
	routine_id VARCHAR(64) NOT NULL, 
	position INTEGER NOT NULL, 
	gesture_id VARCHAR(64) NOT NULL, 
	prompt VARCHAR(200) NOT NULL, 
	hint VARCHAR(300) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(routine_id) REFERENCES routines (id)
);

CREATE INDEX ix_routine_steps_routine_id ON routine_steps (routine_id);

CREATE TABLE achievements (
	id INTEGER NOT NULL, 
	profile_id VARCHAR(64) NOT NULL, 
	code VARCHAR(48) NOT NULL, 
	title VARCHAR(120) NOT NULL, 
	description VARCHAR(300) NOT NULL, 
	unlocked_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_achievement_profile_code UNIQUE (profile_id, code), 
	FOREIGN KEY(profile_id) REFERENCES profiles (id)
);

CREATE INDEX ix_achievements_profile_id ON achievements (profile_id);

CREATE TABLE educator_group_members (
	id INTEGER NOT NULL, 
	group_id VARCHAR(64) NOT NULL, 
	profile_id VARCHAR(64) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_group_member UNIQUE (group_id, profile_id), 
	FOREIGN KEY(group_id) REFERENCES educator_groups (id), 
	FOREIGN KEY(profile_id) REFERENCES profiles (id)
);

CREATE INDEX ix_educator_group_members_profile_id ON educator_group_members (profile_id);

CREATE INDEX ix_educator_group_members_group_id ON educator_group_members (group_id);

CREATE TABLE progress_logs (
	id INTEGER NOT NULL, 
	profile_id VARCHAR(64) NOT NULL, 
	routine_id VARCHAR(64) NOT NULL, 
	gesture_id VARCHAR(64) NOT NULL, 
	accuracy FLOAT NOT NULL, 
	band VARCHAR(16) NOT NULL, 
	attempts INTEGER NOT NULL, 
	succeeded BOOLEAN NOT NULL, 
	completed_routine BOOLEAN NOT NULL, 
	incorrect_points JSON NOT NULL, 
	tz_offset_minutes INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(profile_id) REFERENCES profiles (id)
);

CREATE INDEX ix_progress_logs_profile_id ON progress_logs (profile_id);

CREATE TABLE progress_state (
	profile_id VARCHAR(64) NOT NULL, 
	current_streak INTEGER NOT NULL, 
	longest_streak INTEGER NOT NULL, 
	last_active_date DATE, 
	total_xp INTEGER NOT NULL, 
	perfect_steps INTEGER NOT NULL, 
	daily_date DATE, 
	daily_progress INTEGER NOT NULL, 
	daily_target INTEGER NOT NULL, 
	total_attempts INTEGER NOT NULL, 
	successes INTEGER NOT NULL, 
	accuracy_sum FLOAT NOT NULL, 
	best_accuracy FLOAT NOT NULL, 
	tz_offset_minutes INTEGER NOT NULL, 
	routines_completed JSON NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (profile_id), 
	FOREIGN KEY(profile_id) REFERENCES profiles (id)
);

CREATE TABLE study_sessions (
	id INTEGER NOT NULL, 
	profile_id VARCHAR(64) NOT NULL, 
	deck VARCHAR(32) NOT NULL, 
	mode VARCHAR(16) NOT NULL, 
	cards_seen INTEGER NOT NULL, 
	correct INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(profile_id) REFERENCES profiles (id)
);

CREATE INDEX ix_study_sessions_profile_id ON study_sessions (profile_id);
