CREATE TABLE isadmin (
    uid varchar(64),
    isadmin bool not null default 0,
    FOREIGN KEY (uid) REFERENCES users(uid),
    PRIMARY KEY (uid))
    ENGINE=MyISAM DEFAULT CHARSET=latin1;;
CREATE TABLE certificates (
    uid varchar(64),
    privatekey char(200) not null,
    publickey char(200) not null,
    is_revoked bool not null default 0,
    FOREIGN KEY (uid) REFERENCES users(uid))
    ENGINE=MyISAM DEFAULT CHARSET=latin1;

insert into isadmin select uid,0 from users;

create user certmanager@localhost identified by 'SniaVj5YQnKSXXVu';
grant insert on imovies.users to certmanager@localhost;
grant insert on imovies.isadmin to certmanager@localhost;
grant insert on imovies.certificates to certmanager@localhost;
grant update on imovies.users to certmanager@localhost;
grant update on imovies.isadmin to certmanager@localhost;
grant update on imovies.certificates to certmanager@localhost;
grant select on imovies.users to certmanager@localhost;
grant select on imovies.isadmin to certmanager@localhost;
grant select on imovies.certificates to certmanager@localhost;

flush privileges;