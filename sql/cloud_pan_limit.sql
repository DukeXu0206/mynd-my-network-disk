

DROP TABLE IF EXISTS `pan_limit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pan_limit` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  `remark` longtext NOT NULL,
  `limit_name` varchar(50) NOT NULL,
  `limit_key` varchar(50) NOT NULL,
  `create_by_id` int DEFAULT NULL,
  `update_by_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `limit_key` (`limit_key`),
  KEY `pan_limit_create_by_id_1658fc3e_fk_auth_user_id` (`create_by_id`),
  KEY `pan_limit_update_by_id_7c9d389d_fk_auth_user_id` (`update_by_id`),
  CONSTRAINT `pan_limit_create_by_id_1658fc3e_fk_auth_user_id` FOREIGN KEY (`create_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `pan_limit_update_by_id_7c9d389d_fk_auth_user_id` FOREIGN KEY (`update_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pan_limit`
--

LOCK TABLES `pan_limit` WRITE;
/*!40000 ALTER TABLE `pan_limit` DISABLE KEYS */;
INSERT INTO `pan_limit` VALUES (1,'2021-12-07 10:23:48.512287','2021-12-07 10:43:45.430604','','云盘容量','storage',1,1),(5,'2023-01-19 06:01:23.714546','2023-01-19 06:01:23.714546','','预览限制','preview',1,1);
/*!40000 ALTER TABLE `pan_limit` ENABLE KEYS */;
UNLOCK TABLES;

