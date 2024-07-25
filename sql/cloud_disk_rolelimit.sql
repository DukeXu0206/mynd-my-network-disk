DROP TABLE IF EXISTS `disk_rolelimit`;

CREATE TABLE `disk_rolelimit` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `remark` longtext NOT NULL,
  `value` bigint NOT NULL,
  `create_by_id` int DEFAULT NULL,
  `limit_id` bigint NOT NULL,
  `role_id` bigint NOT NULL,
  `update_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `disk_rolelimit_create_by_id_f7391961_fk_auth_user_id` (`create_by_id`),
  KEY `disk_rolelimit_limit_id_f8b193ad_fk_disk_limit_id` (`limit_id`),
  KEY `disk_rolelimit_role_id_6f78abcf_fk_disk_role_id` (`role_id`),
  KEY `disk_rolelimit_update_by_id_6710b13d_fk_auth_user_id` (`update_by_id`),
  CONSTRAINT `disk_rolelimit_create_by_id_f7391961_fk_auth_user_id` FOREIGN KEY (`create_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `disk_rolelimit_limit_id_f8b193ad_fk_disk_limit_id` FOREIGN KEY (`limit_id`) REFERENCES `disk_limit` (`id`),
  CONSTRAINT `disk_rolelimit_role_id_6f78abcf_fk_disk_role_id` FOREIGN KEY (`role_id`) REFERENCES `disk_role` (`id`),
  CONSTRAINT `disk_rolelimit_update_by_id_6710b13d_fk_auth_user_id` FOREIGN KEY (`update_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


LOCK TABLES `disk_rolelimit` WRITE;
INSERT INTO `disk_rolelimit` VALUES
(1, NOW(6), NOW(6), '', 8589934592, 1, 1, 1, 1),
(4, NOW(6), NOW(6), '', 8589934592, 1, 1, 2, 1),
(7, NOW(6), NOW(6), '', 5368709120, 1, 1, 3, 1),
(13, NOW(6), NOW(6), '', 20971520, 1, 5, 3, 1),
(14, NOW(6), NOW(6), '', 41943040, 1, 5, 2, 1),
(15, NOW(6), NOW(6), '', 41943040, 1, 5, 1, 1);
UNLOCK TABLES;
