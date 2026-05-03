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
    UNIQUE(user_id, position)
);
