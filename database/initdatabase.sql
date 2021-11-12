CREATE TABLE isadmin (
    uid varchar(64),
    isadmin bool not null default 0,
    FOREIGN KEY (uid) REFERENCES users(uid),
    PRIMARY KEY (uid))
    ENGINE=MyISAM DEFAULT CHARSET=latin1;;
CREATE TABLE certificates (
    uid varchar(64),
    publickey char(200) not null,
    is_revoked bool not null default 0,
    FOREIGN KEY (uid) REFERENCES users(uid))
    ENGINE=MyISAM DEFAULT CHARSET=latin1;

create user certmanager@172.27.0.1 identified by 'SniaVj5YQnKSXXVu';
grant insert on imovies.users to certmanager@172.27.0.1;
grant insert on imovies.isadmin to certmanager@172.27.0.1;
grant insert on imovies.certificates to certmanager@172.27.0.1;
grant update on imovies.users to certmanager@172.27.0.1;
grant update on imovies.isadmin to certmanager@172.27.0.1;
grant update on imovies.certificates to certmanager@172.27.0.1;
grant select on imovies.users to certmanager@172.27.0.1;
grant select on imovies.isadmin to certmanager@172.27.0.1;
grant select on imovies.certificates to certmanager@172.27.0.1;

create user certmanager@172.27.0.2 identified by 'SniaVj5YQnKSXXVu';
grant insert on imovies.users to certmanager@172.27.0.2;
grant insert on imovies.isadmin to certmanager@172.27.0.2;
grant insert on imovies.certificates to certmanager@172.27.0.2;
grant update on imovies.users to certmanager@172.27.0.2;
grant update on imovies.isadmin to certmanager@172.27.0.2;
grant update on imovies.certificates to certmanager@172.27.0.2;
grant select on imovies.users to certmanager@172.27.0.2;
grant select on imovies.isadmin to certmanager@172.27.0.2;
grant select on imovies.certificates to certmanager@172.27.0.2;
flush privileges;

insert into isadmin select uid,0 from users;

delimiter |
CREATE TRIGGER isadminInsert AFTER INSERT ON users
    FOR EACH ROW
BEGIN
    INSERT INTO isadmin values (new.uid, 0);
END; |
delimiter ;

