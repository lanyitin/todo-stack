create table if not exists stack( 
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
create table if not exists todo( 
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    content TEXT NOT NULL,
    `order` INTEGER default 0,
    stackid INTEGER NOT NULL,
    priority INTEGER NOT NULL
);
