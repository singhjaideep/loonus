drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  original text not null,
  shorturl text not null
);