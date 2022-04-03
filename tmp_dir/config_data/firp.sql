-- firp_user
CREATE TABLE
IF
	NOT EXISTS firp_user (
		sub VARCHAR ( 255 ) NOT NULL,
		colum_key VARCHAR ( 255 ) NOT NULL,
		colum_val VARCHAR ( 255 ) NOT NULL,
		INDEX sub_index ( `sub` )
	) ENGINE = INNODB DEFAULT CHARSET = UTF8MB4;

-- fund_similarity_port
CREATE TABLE
IF
	NOT EXISTS fund_similarity_port (
	    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	    sub VARCHAR (255) NOT NULL,
	    owner VARCHAR (255) NOT NULL,
	    ticker VARCHAR (255) NOT NULL,
	    port_name VARCHAR (255) NOT NULL,
	    port_size VARCHAR (255) NOT NULL,
	    compute_date VARCHAR (255) NOT NULL,
        similarity_data MEDIUMTEXT NOT NULL,
        similarity_error FLOAT NOT NULL,
        create_time TIMESTAMP NOT NULL,
        INDEX sub_index ( `sub` ),
        INDEX port_name_index ( `port_name` )
	) ENGINE = INNODB DEFAULT CHARSET = UTF8MB4;


-- firp_user data
INSERT INTO `zhaofan`.`firp_user` (`sub`, `colum_key`, `colum_val`) VALUES ('8016f9f3-6821-42f3-9696-5a2da1469370', 'username', 'user_1');
INSERT INTO `zhaofan`.`firp_user` (`sub`, `colum_key`, `colum_val`) VALUES ('8016f9f3-6821-42f3-9696-5a2da1469370', 'company', 'deepred');
INSERT INTO `zhaofan`.`firp_user` (`sub`, `colum_key`, `colum_val`) VALUES ('8016f9f3-6821-42f3-9696-5a2da1469370', 'access', 'admin');
INSERT INTO `zhaofan`.`firp_user` (`sub`, `colum_key`, `colum_val`) VALUES ('c0c86fed-4dfa-4f59-80de-5142cf1c1b26', 'username', 'user_2');
INSERT INTO `zhaofan`.`firp_user` (`sub`, `colum_key`, `colum_val`) VALUES ('c0c86fed-4dfa-4f59-80de-5142cf1c1b26', 'company', 'deepred');
INSERT INTO `zhaofan`.`firp_user` (`sub`, `colum_key`, `colum_val`) VALUES ('c0c86fed-4dfa-4f59-80de-5142cf1c1b26', 'access', 'user');
INSERT INTO `zhaofan`.`firp_user` (`sub`, `colum_key`, `colum_val`) VALUES ('48b5f145-ade3-4d1d-a0eb-df99def2e12b', 'username', 'user_3');
INSERT INTO `zhaofan`.`firp_user` (`sub`, `colum_key`, `colum_val`) VALUES ('48b5f145-ade3-4d1d-a0eb-df99def2e12b', 'company', 'deepred');
INSERT INTO `zhaofan`.`firp_user` (`sub`, `colum_key`, `colum_val`) VALUES ('48b5f145-ade3-4d1d-a0eb-df99def2e12b', 'access', 'user');


-- fund_similarity_port data
INSERT INTO `zhaofan`.`fund_similarity_port` ( `id`, `sub`, `owner`, `ticker`, `port_name`, `port_size`, `compute_date`, `similarity_data`, `similarity_error`, `create_time` )
VALUES
	( 1, '8016f9f3-6821-42f3-9696-5a2da1469370', '8016f9f3-6821-42f3-9696-5a2da1469370', '001384.OF', 'new_port_01', '2', '2022-02-14', '[{\"fund_code\": \"184688.OF\", \"fund_name\": \"\\u5357\\u65b9\\u5f00\\u5143\\u5c01\\u95ed\", \"weight\": 0.4}, {\"fund_code\": \"184689.OF\", \"fund_name\": \"\\u9e4f\\u534e\\u666e\\u60e0\\u5c01\\u95ed\", \"weight\": 0.4}, {\"fund_code\": \"184690.OF\", \"fund_name\": \"\\u957f\\u76db\\u540c\\u76ca\\u5c01\\u95ed\", \"weight\": 0.2}]', 0.37, '2022-02-14 14:49:01' );