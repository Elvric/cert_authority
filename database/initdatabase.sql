CREATE TABLE isadmin (
    uid varchar(64),
    isadmin bool not null default 0,
    FOREIGN KEY (uid) REFERENCES users(uid),
    PRIMARY KEY (uid))
    ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE certificates (
    serial int,
    uid varchar(64),
    pem_encoding varchar(32768) not null,
    revoked bool not null default 0,
    FOREIGN KEY (uid) REFERENCES users(uid),
    PRIMARY KEY (serial))
    ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE certificate_issuing_status
(
    rid int,
    serial int,
    issued int,
    revoked int,
    PRIMARY KEY (rid))
    ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- TODO remove that user
create user test@'%' identified by 'SniaVj5YQnKSXXVu';
grant all privileges on *.* to test@'%' with grant option;

create user certmanager@172.27.0.2 identified by 'SniaVj5YQnKSXXVu';
grant insert on imovies.users to certmanager@172.27.0.2;
grant insert on imovies.certificate_issuing_status to certmanager@172.27.0.2;
grant insert on imovies.isadmin to certmanager@172.27.0.2;
grant insert on imovies.certificates to certmanager@172.27.0.2;
grant update on imovies.users to certmanager@172.27.0.2;
grant update on imovies.isadmin to certmanager@172.27.0.2;
grant update on imovies.certificates to certmanager@172.27.0.2;
grant update on imovies.certificate_issuing_status to certmanager@172.27.0.2;
grant select on imovies.users to certmanager@172.27.0.2;
grant select on imovies.isadmin to certmanager@172.27.0.2;
grant select on imovies.certificates to certmanager@172.27.0.2;
grant select on imovies.certificate_issuing_status to certmanager@172.27.0.2;
flush privileges;

insert into isadmin select uid,0 from users;
update isadmin SET isadmin=1 WHERE uid="ps";

delimiter |
CREATE TRIGGER isadminInsert AFTER INSERT ON users
    FOR EACH ROW
BEGIN
    INSERT INTO isadmin values (new.uid, 0);
END; |
delimiter ;

