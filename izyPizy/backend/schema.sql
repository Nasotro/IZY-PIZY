CREATE TABLE IF NOT EXISTS dictionary_numbers (
    number TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS dictionary_words (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT    NOT NULL,
    number TEXT    NOT NULL,
    word   TEXT    NOT NULL,
    UNIQUE(user_id, number, word)
);

CREATE TABLE IF NOT EXISTS stories (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  TEXT    NOT NULL,
    position INTEGER NOT NULL,
    sentence TEXT,
    word_0   TEXT NOT NULL,
    word_1   TEXT NOT NULL,
    word_2   TEXT NOT NULL,
    word_3   TEXT NOT NULL,
    word_4   TEXT NOT NULL,
    image_path TEXT,
    video_path TEXT,
    start_frame_path TEXT,
    end_frame_path TEXT,
    visual_kind TEXT,
    UNIQUE(user_id, position)
);

-- One icon per distinct word, shared by every dictionary entry spelling it the
-- same way (the same word can sit under several two-digit numbers).
CREATE TABLE IF NOT EXISTS word_icons (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          TEXT    NOT NULL,
    word_key         TEXT    NOT NULL,
    image_path       TEXT    NOT NULL,
    user_description TEXT,
    prompt           TEXT,
    model            TEXT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT,
    UNIQUE(user_id, word_key)
);
