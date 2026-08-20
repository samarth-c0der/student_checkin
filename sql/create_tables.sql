-- =====================================================
-- STUDENTS
-- Stores information about each student
-- =====================================================

CREATE TABLE IF NOT EXISTS STUDENTS (
    student_id INTEGER AUTOINCREMENT PRIMARY KEY,
    student_name VARCHAR NOT NULL,
    slack_user_id VARCHAR NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- =====================================================
-- CHANNELS
-- Maps Slack channels to students
-- =====================================================

CREATE TABLE IF NOT EXISTS CHANNELS (
    channel_id VARCHAR PRIMARY KEY,
    channel_name VARCHAR NOT NULL UNIQUE,
    student_id INTEGER NOT NULL,
    last_processed_ts VARCHAR,

    CONSTRAINT fk_student
        FOREIGN KEY (student_id)
        REFERENCES STUDENTS(student_id)
);


-- =====================================================
-- CHECKIN_HISTORY
-- Stores every AI-generated analysis
-- =====================================================

CREATE TABLE IF NOT EXISTS CHECKIN_HISTORY (

    analysis_id INTEGER AUTOINCREMENT PRIMARY KEY,

    student_id INTEGER NOT NULL,

    channel_id VARCHAR NOT NULL,

    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

    prompt VARCHAR,

    raw_response VARCHAR,

    analysis_json VARCHAR,

    checkin_message VARCHAR,

    CONSTRAINT fk_student_analysis
        FOREIGN KEY (student_id)
        REFERENCES STUDENTS(student_id),

    CONSTRAINT fk_channel_analysis
        FOREIGN KEY (channel_id)
        REFERENCES CHANNELS(channel_id)
);