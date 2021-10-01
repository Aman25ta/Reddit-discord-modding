CREATE schema if not exists reddit_posted;

CREATE TABLE if not exists reddit_posted.rising (
	postid VARCHAR ( 50 ) NOT NULL PRIMARY KEY,
	reddit_username VARCHAR ( 50 ) NOT NULL,
	mod_id VARCHAR ( 50 ),
	action VARCHAR ( 50 )
);

alter table reddit_posted.rising
    owner to postgres;
	
CREATE TABLE if not exists reddit_posted.hot (
	postid VARCHAR ( 50 ) NOT NULL PRIMARY KEY,
	reddit_username VARCHAR ( 50 ) NOT NULL,
	mod_id VARCHAR ( 50 ),
	action VARCHAR ( 50 )
);

alter table reddit_posted.hot
    owner to postgres;
