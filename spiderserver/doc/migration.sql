drop table if exists frontserver_user;
CREATE TABLE `frontserver_user` (
  `id` int(11) AUTO_INCREMENT,
  `username` varchar(24) DEFAULT '',
  `nick_name` varchar(24) DEFAULT '',
  `hashed_password` varchar(128) DEFAULT '',
  `password_salt` varchar(40) DEFAULT '',
  `perishable_token` varchar(50) DEFAULT '',
  `register_time` datetime DEFAULT '1982-12-06 00:00:00',
  `register_ip` int(11) DEFAULT '0',
  `failed_login_count` int(11) DEFAULT '0',
  `current_login_ip` varchar(15) DEFAULT '',
  `last_login_time` datetime DEFAULT '1982-12-06 00:00:00',
  `last_request_time` datetime DEFAULT '1982-12-06 00:00:00',
  `last_login_ip` varchar(15) DEFAULT '',
  `email` varchar(40) DEFAULT '',
  `phone_number` varchar(15) default '',
  `phone_ime` varchar(200) default '',
  `status` int(11) DEFAULT '0',
  `user_type` tinyint(4) DEFAULT '0',
  `user_auth` int(11) DEFAULT '0',
  `gender` smallint(6) DEFAULT '0',
  `birthday` date DEFAULT '1982-12-06',
  `avatar` varchar(40) DEFAULT '',
  `city_id` int(11) DEFAULT '0',
  `district_id` int(11) DEFAULT '0',
  `subscribe_status` smallint(6) DEFAULT '0',
  `online_time` int(11) DEFAULT '0',
  `invite_code` varchar(20) DEFAULT '',
  `identity_status` tinyint(4) DEFAULT '0',
  `password_to_reset` varchar(128) default '',
  PRIMARY KEY (`id`)
);

/*
修改说明：
1. 订阅的提交时间，就是这条记录的创建时间=created_at，这个是通用的，基本上需要这个功能的都这么表示；
2. 订阅的状态等，用status来表示，凡是用来记录状态的，都用这个来表示，基本通用
3. 订阅的关闭时间，用最后修改时间=updated_at来表示，这个也是通用的
4. 仔细斟酌，还是把价格名称设计为 min_price max_price,这样符合习惯
5. 其他的有几个换成了 xxx_id
   基本不做表的关联了，尤其是city, brand等，这些生产环境下，是常驻内存的
*/
drop table if exists frontserver_photograph_subscribe;
create table `frontserver_photograph_subscribe` (
  `id` int(11) auto_increment,
  `user_id` int(11) not null,
  `business_id` int(11) not null,
  `city_id` int(11) default 0,
  `district_id` int(11) default 0,
  `brand_id` int(11) default 0,
  `min_price` int(11) default 0,
  `max_price` int(11) default 0,
  `keyword` varchar(100) default '',
  `created_at` datetime default '1970-01-01 00:00:00',
  `updated_at` datetime default '1970-01-01 00:00:00',
  `status` int(2) default 0,
  `notify_count` int(11) default 0,
  primary key (`id`),
  key `frontserver_photograph_subscribe_403f60f` (`user_id`),
  key `frontserver_photograph_subscribe_4df04126` (`business_id`)
);




