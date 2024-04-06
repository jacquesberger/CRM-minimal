create table entreprise (
  id integer primary key,
  nom varchar
);

create table interaction (
  id integer primary key,
  description varchar,
  moment varchar,
  entreprise_id integer,
  foreign key(entreprise_id) references entreprise(id)
);

create table rappel (
  id integer primary key,
  done integer,
  activation date,
  note varchar,
  entreprise_id integer,
  foreign key(entreprise_id) references entreprise(id)
);
