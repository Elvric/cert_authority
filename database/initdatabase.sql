CREATE TABLE isadmin (
    uid varchar(64),
    isCaAdmin bool not null default 0,
    isSysAdmin bool not null default 0,
    FOREIGN KEY (uid) REFERENCES users(uid),
    PRIMARY KEY (uid))
    ENGINE=MyISAM DEFAULT CHARSET=latin1;;
CREATE TABLE certificates (
    serial int not null,
    uid varchar(64),
    publickey char(200) not null,
    is_revoked bool not null default 0,
    FOREIGN KEY (uid) REFERENCES users(uid))
    PRIMARY KEY (serial)
    ENGINE=MyISAM DEFAULT CHARSET=latin1;

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

insert into isadmin select uid,0 from users;

delimiter |
CREATE TRIGGER isadminInsert AFTER INSERT ON users
    FOR EACH ROW
BEGIN
    INSERT INTO isadmin values (new.uid, 0);
END; |
delimiter ;

